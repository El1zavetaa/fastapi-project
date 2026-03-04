from fastapi import APIRouter

from .books import books_router
from .seller import seller_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(books_router)
v1_router.include_router(seller_router)