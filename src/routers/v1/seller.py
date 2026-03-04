from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas.seller import (
    IncomingSeller,
    ReturnedSeller,
    ReturnedSellerWithBooks,
    ReturnedAllSellers,
    UpdateSeller,
)
from src.services import SellerService

seller_router = APIRouter(prefix="/seller", tags=["seller"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@seller_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    """Регистрация нового продавца"""
    new_seller = await SellerService(session).create_seller(seller)
    return new_seller


@seller_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    """Получение списка всех продавцов (без паролей)"""
    sellers = await SellerService(session).get_all_sellers()
    return {"sellers": sellers}


@seller_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller_by_id(seller_id: int, session: DBSession):
    """Получение данных о конкретном продавце со списком его книг"""
    seller = await SellerService(session).get_seller_by_id(seller_id, with_books=True)

    if seller is not None:
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@seller_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: UpdateSeller, session: DBSession):
    """Обновление данных о продавце (без пароля)"""
    updated_seller = await SellerService(session).update_seller(seller_id, seller_data)

    if updated_seller is not None:
        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@seller_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    """Удаление продавца и всех его книг"""
    deleted = await SellerService(session).delete_seller(seller_id)

    if not deleted:
        return Response(status_code=status.HTTP_404_NOT_FOUND)