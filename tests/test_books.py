import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book

API_V1_URL_PREFIX = "/api/v1/books"


# Тест на ручку создающую книгу
@pytest.mark.asyncio()
async def test_create_book(async_client, test_seller):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": test_seller.id
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id is not None, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": test_seller.id
    }


# Тест на ручку создающую книгу со старым годом
@pytest.mark.asyncio()
async def test_create_book_with_old_year(async_client, test_seller):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
        "seller_id": test_seller.id
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка книг
@pytest.mark.asyncio()
async def test_get_books(db_session, async_client, test_seller):
    # Создаем книги вручную
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=test_seller.id
    )
    book_2 = Book(
        author="Lermontov",
        title="Mziri",
        year=2021,
        pages=108,
        seller_id=test_seller.id
    )

    db_session.add_all([book, book_2])
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["books"]) == 2

    # Проверяем наличие seller_id
    for book_data in data["books"]:
        assert "seller_id" in book_data
        assert book_data["seller_id"] == test_seller.id


# Тест на ручку получения одной книги
@pytest.mark.asyncio()
async def test_get_single_book(db_session, async_client, test_seller):
    # Создаем книгу
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=test_seller.id
    )

    db_session.add(book)
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["title"] == "Eugeny Onegin"
    assert result["author"] == "Pushkin"
    assert result["year"] == 2001
    assert result["pages"] == 104
    assert result["seller_id"] == test_seller.id


# Тест на ручку получения несуществующей книги
@pytest.mark.asyncio()
async def test_get_single_book_with_wrong_id(db_session, async_client, test_seller):
    # Создаем книгу
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=test_seller.id
    )

    db_session.add(book)
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку обновления книги
@pytest.mark.asyncio()
async def test_update_book(db_session, async_client, test_seller):
    # Создаем книгу
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=test_seller.id
    )

    db_session.add(book)
    await db_session.commit()

    update_data = {
        "title": "New Title",
        "author": "New Author",
        "pages": 200,
        "year": 2024,
        "id": book.id,
        "seller_id": test_seller.id
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK

    # Проверяем обновление
    await db_session.refresh(book)
    assert book.title == "New Title"
    assert book.author == "New Author"
    assert book.pages == 200
    assert book.year == 2024
    assert book.seller_id == test_seller.id


# Тест на удаление книги
@pytest.mark.asyncio()
async def test_delete_book(db_session, async_client, test_seller):
    # Создаем книгу
    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=test_seller.id
    )

    db_session.add(book)
    await db_session.commit()
    book_id = book.id  # Сохраняем ID книги

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Сбрасываем сессию и проверяем, что книга действительно удалена из БД
    await db_session.commit()  # Фиксируем изменения
    await db_session.close()  # Закрываем старую сессию

    # Создаем новую сессию или используем существующую с очисткой
    # Проверяем, что книга удалена
    deleted_book = await db_session.get(Book, book_id)
    assert deleted_book is None


# Тест на удаление несуществующей книги
@pytest.mark.asyncio()
async def test_delete_book_with_invalid_book_id(db_session, async_client, test_seller):
    # Создаем книгу
    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=test_seller.id
    )

    db_session.add(book)
    await db_session.commit()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND