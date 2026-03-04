import requests
import json

# Создать книгу
new_book = {
    "title": "Clean Architecture",
    "author": "Robert Martin",
    "count_pages": 300,
    "year": 2025
}

response = requests.post("http://localhost:8000/books", json=new_book)
print("Create:", response.json())

# Получить список
response = requests.get("http://localhost:8000/books")
print("All books:", response.json())