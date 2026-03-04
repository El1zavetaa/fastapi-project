__all__ = ["SellerService"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.seller import Seller
from src.models.books import Book
from src.schemas.seller import IncomingSeller, UpdateSeller, ReturnedSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_seller(self, seller_data: IncomingSeller) -> Seller:
        """Создание нового продавца"""
        new_seller = Seller(
            first_name=seller_data.first_name,
            last_name=seller_data.last_name,
            e_mail=seller_data.e_mail,
            password=seller_data.password  # В реальном проекте пароль нужно хешировать!
        )
        self.session.add(new_seller)
        await self.session.flush()
        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        """Получение списка всех продавцов"""
        query = select(Seller)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_seller_by_id(self, seller_id: int, with_books: bool = False) -> Seller | None:
        """Получение продавца по ID"""
        if with_books:
            query = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        else:
            return await self.session.get(Seller, seller_id)

    async def update_seller(self, seller_id: int, seller_data: UpdateSeller) -> Seller | None:
        """Обновление данных продавца (без пароля)"""
        seller = await self.session.get(Seller, seller_id)
        if seller:
            if seller_data.first_name is not None:
                seller.first_name = seller_data.first_name
            if seller_data.last_name is not None:
                seller.last_name = seller_data.last_name
            if seller_data.e_mail is not None:
                seller.e_mail = seller_data.e_mail

            await self.session.flush()
            return seller
        return None

    async def delete_seller(self, seller_id: int) -> bool:
        """Удаление продавца и всех его книг"""
        seller = await self.session.get(Seller, seller_id)
        if seller:
            await self.session.delete(seller)
            return True
        return False