import pytest
from fastapi import status
from sqlalchemy import select

from src.models.seller import Seller
from src.models.books import Book

API_V1_URL_PREFIX = "/api/v1/seller"


# ТЕСТ 1: Создание продавца
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    """Тест успешного создания продавца"""
    data = {
        "first_name": "Иван",
        "last_name": "Петров",
        "e_mail": "ivan@example.com",
        "password": "password123"
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    # Проверяем, что id вернулся
    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id is not None, "Seller id not returned from endpoint"

    # Проверяем, что пароль НЕ вернулся
    assert "password" not in result_data

    # Проверяем остальные поля
    assert result_data == {
        "first_name": "Иван",
        "last_name": "Петров",
        "e_mail": "ivan@example.com"
    }


# ТЕСТ 2: Создание продавца с невалидным email
@pytest.mark.asyncio()
async def test_create_seller_invalid_email(async_client):
    """Тест создания продавца с неправильным email"""
    data = {
        "first_name": "Иван",
        "last_name": "Петров",
        "e_mail": "not-an-email",
        "password": "password123"
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ТЕСТ 3: Создание продавца с коротким паролем
@pytest.mark.asyncio()
async def test_create_seller_short_password(async_client):
    """Тест создания продавца с коротким паролем"""
    data = {
        "first_name": "Иван",
        "last_name": "Петров",
        "e_mail": "ivan@example.com",
        "password": "123"
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ТЕСТ 4: Получение списка всех продавцов
@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    """Тест получения списка всех продавцов"""
    # Создаем продавцов вручную
    import uuid
    seller1 = Seller(
        first_name="Иван",
        last_name="Петров",
        e_mail=f"ivan_{uuid.uuid4()}@example.com",
        password="hash123"
    )
    seller2 = Seller(
        first_name="Мария",
        last_name="Сидорова",
        e_mail=f"maria_{uuid.uuid4()}@example.com",
        password="hash456"
    )

    db_session.add_all([seller1, seller2])
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "sellers" in data
    assert len(data["sellers"]) >= 2

    # Проверяем, что у продавцов нет поля password
    for seller in data["sellers"]:
        assert "password" not in seller


# ТЕСТ 5: Получение одного продавца по ID
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client):
    """Тест получения одного продавца"""
    # Создаем продавца
    import uuid
    seller = Seller(
        first_name="Иван",
        last_name="Петров",
        e_mail=f"ivan_{uuid.uuid4()}@example.com",
        password="hash123"
    )

    db_session.add(seller)
    await db_session.commit()

    # Создаем книгу для этого продавца
    book = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller_id=seller.id
    )
    db_session.add(book)
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    # Проверяем, что пароль не вернулся
    assert "password" not in result_data

    # Проверяем, что книги вернулись
    assert "books" in result_data
    assert len(result_data["books"]) == 1
    assert result_data["books"][0]["seller_id"] == seller.id


# ТЕСТ 6: Получение несуществующего продавца
@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(db_session, async_client):
    """Тест получения продавца с несуществующим ID"""
    import uuid
    seller = Seller(
        first_name="Иван",
        last_name="Петров",
        e_mail=f"ivan_{uuid.uuid4()}@example.com",
        password="hash123"
    )

    db_session.add(seller)
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# ТЕСТ 7: Обновление продавца
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    """Тест обновления данных продавца"""
    # Создаем продавца
    import uuid
    seller = Seller(
        first_name="Иван",
        last_name="Петров",
        e_mail=f"ivan_{uuid.uuid4()}@example.com",
        password="hash123"
    )

    db_session.add(seller)
    await db_session.commit()

    # Данные для обновления (без пароля)
    update_data = {
        "first_name": "Петр",
        "last_name": "Иванов",
        "e_mail": f"petr_{uuid.uuid4()}@example.com"
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    # Проверяем, что пароль не вернулся
    assert "password" not in result_data

    # Проверяем в БД
    await db_session.refresh(seller)
    assert seller.first_name == "Петр"
    assert seller.last_name == "Иванов"
    # Пароль не должен измениться
    assert seller.password == "hash123"


# ТЕСТ 8: Удаление продавца
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    """Тест удаления продавца"""
    # Создаем продавца
    import uuid
    seller = Seller(
        first_name="Иван",
        last_name="Петров",
        e_mail=f"ivan_{uuid.uuid4()}@example.com",
        password="hash123"
    )

    db_session.add(seller)
    await db_session.commit()
    seller_id = seller.id  # Сохраняем ID продавца

    # Создаем книгу для этого продавца
    book = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller_id=seller_id
    )
    db_session.add(book)
    await db_session.commit()
    book_id = book.id  # Сохраняем ID книги

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Очищаем кэш сессии
    await db_session.commit()
    db_session.expire_all()  # Очищаем все объекты из кэша сессии

    # Проверяем, что продавец удален
    deleted_seller = await db_session.get(Seller, seller_id)
    assert deleted_seller is None

    # Проверяем, что книги тоже удалены (каскадное удаление)
    deleted_book = await db_session.get(Book, book_id)
    assert deleted_book is None


# ТЕСТ 9: Удаление несуществующего продавца
@pytest.mark.asyncio()
async def test_delete_seller_with_wrong_id(db_session, async_client):
    """Тест удаления несуществующего продавца"""
    import uuid
    seller = Seller(
        first_name="Иван",
        last_name="Петров",
        e_mail=f"ivan_{uuid.uuid4()}@example.com",
        password="hash123"
    )

    db_session.add(seller)
    await db_session.commit()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND