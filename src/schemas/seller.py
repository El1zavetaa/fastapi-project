from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from src.schemas.books import ReturnedBook

__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
    "UpdateSeller",
]


# Базовая схема продавца (без пароля)
class BaseSeller(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    e_mail: EmailStr


# Схема для создания продавца (с паролем)
class IncomingSeller(BaseSeller):
    password: str = Field(..., min_length=6, max_length=100)


# Схема для возврата данных о продавце (без пароля)
class ReturnedSeller(BaseSeller):
    id: int


# Схема для возврата продавца с его книгами
class ReturnedSellerWithBooks(ReturnedSeller):
    books: List[ReturnedBook] = []


# Схема для возврата списка продавцов
class ReturnedAllSellers(BaseModel):
    sellers: List[ReturnedSeller]


# Схема для обновления данных продавца (без пароля и книг)
class UpdateSeller(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    e_mail: Optional[EmailStr] = None