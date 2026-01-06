from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query
from collections import Counter
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db, BookDB
from typing import List
from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth import verify_api_key
from database import get_db, BookDB  

# Создание экземпляра приложения FastAPI
app = FastAPI(
    title="Books API",
    description="REST API для управления библиотекой книг",
    version="1.0.0"
)

# Модель данных для книги (Pydantic схема)
class Book(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200, description="Название книги")
    author: str = Field(..., min_length=1, max_length=100, description="Автор книги")
    year: int = Field(..., ge=1000, le=datetime.now().year, description="Год издания")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN книги")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Мастер и Маргарита",
                "author": "Михаил Булгаков",
                "year": 1967,
                "isbn": "9785170123456"
            }
        }

# Модель для обновления книги (все поля опциональны)
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)

# Временное хранилище данных (в реальном приложении используется база данных)
books_db: List[Book] = [
    Book(id=1, title="Война и мир", author="Лев Толстой", year=1869, isbn="9785170987654"),
    Book(id=2, title="Преступление и наказание", author="Федор Достоевский", year=1866, isbn="9785170876543"),
    Book(id=3, title="Евгений Онегин", author="Александр Пушкин", year=1833, isbn="9785170765432")
]

# Счетчик для генерации ID
next_id = 4

# Корневой эндпоинт
@app.get("/", tags=["Root"])
async def root():
    """
    Корневой эндпоинт API.
    Возвращает приветственное сообщение и ссылки на документацию.
    """
    return {
        "message": "Добро пожаловать в Books API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/books", response_model=List[Book], tags=["Books"])
async def get_books(db: Session = Depends(get_db)):
    """Получить список всех книг из базы данных."""
    books = db.query(BookDB).all()
    return books

@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(book: Book,api_key: str = Depends(verify_api_key)):
    """Создать новую книгу в базе данных."""

    data = book.dict(exclude={"id"}) if "id" in dir(book) else book.dict()
    db_book = BookDB(**data)

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# GET /api/books - Получение списка всех книг
@app.get("/api/books", response_model=List[Book], tags=["Books"])
async def get_books(
    author: Optional[str] = Query(None, description="Фильтр по автору (частичное совпадение)"),
    year_from: Optional[int] = Query(None, description="Минимальный год издания"),
    year_to: Optional[int] = Query(None, description="Максимальный год издания"),
    skip: int = Query(0, ge=0, description="Количество книг для пропуска (offset)"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество возвращаемых книг")
):
    """

    - **author**: Фильтр по автору (регистронезависимо)
    - **year_from**: Минимальный год издания
    - **year_to**: Максимальный год издания
    - **skip**: Смещение от начала списка
    - **limit**: Ограничение количества результатов
    """
    # 1. Применяем фильтрацию
    filtered_books = books_db

    if author:
        author_lower = author.lower()
        filtered_books = [
            b for b in filtered_books 
            if author_lower in b.author.lower()
        ]

    if year_from:
        filtered_books = [b for b in filtered_books if b.year >= year_from]

    if year_to:
        filtered_books = [b for b in filtered_books if b.year <= year_to]

    # 2. Применяем пагинацию к отфильтрованному списку
    return filtered_books[skip : skip + limit]

# GET /api/books/{book_id} - Получение книги по ID
@app.get("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book(book_id: int):
    """
    Получить книгу по ID.
    - **book_id**: ID книги (целое число)

    Возвращает информацию о книге с указанным ID.
    Если книга не найдена, возвращается ошибка 404.
    """
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )

@app.get("/api/books/stats", tags=["Statistics"])
async def get_statistics():
    """
    Получить статистику по книгам.

    Возвращает:
    - **total_books**: Общее количество книг в базе данных.
    - **books_by_author**: Распределение количества книг по авторам.
    - **books_by_century**: Распределение книг по векам издания.
    """
    total_books = len(books_db)
    
    # Подсчет количества книг по авторам
    authors_counts = Counter(book.author for book in books_db)
    
    # Подсчет книг по векам (например, 1954 // 100 + 1 = 20 век)
    centuries_counts = Counter(book.year // 100 + 1 for book in books_db)
    
    # Формируем читаемый словарь для веков
    stats_by_century = {
        f"{century} век": count 
        for century, count in sorted(centuries_counts.items())
    }

    return {
        "total_books": total_books,
        "books_by_author": dict(authors_counts),
        "books_by_century": stats_by_century
    }

# POST /api/books - Создание новой книги
@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(book: Book):
    """
    Создать новую книгу.
    Принимает данные новой книги и добавляет её в систему.
    Автоматически генерирует уникальный ID для книги.
    Возвращает созданную книгу с присвоенным ID.
    """
    global next_id
    # Присваиваем новый ID
    book.id = next_id
    next_id += 1
    # Добавляем книгу в базу данных
    books_db.append(book)
    return book

# PUT /api/books/{book_id} - Полное обновление книги
@app.put("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def update_book(book_id: int, updated_book: Book):
    """
    Полностью обновить информацию о книге.
    """
    for index, book in enumerate(books_db):
        if book.id == book_id:
            # Сохраняем ID, чтобы он не изменился при обновлении
            updated_book.id = book_id
            books_db[index] = updated_book
            return updated_book
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


# PATCH /api/books/{book_id} - Частичное обновление книги
@app.patch("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def partial_update_book(book_id: int, book_update: BookUpdate):
    """
    Частично обновить информацию о книге.
    
    - **book_id**: ID книги для обновления
    - **book_update**: Данные для обновления (только указанные поля будут изменены)
    """
    for book in books_db:
        if book.id == book_id:
            # Обновляем только те поля, которые были явно переданы в запросе
            update_data = book_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(book, field, value)
            return book
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


# DELETE /api/books/{book_id} - Удаление книги
@app.delete(
    "/api/books/{book_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    tags=["Books"]
)
async def delete_book(book_id: int):
    """
    Удалить книгу по ID.
    
    - **book_id**: ID книги для удаления
    """
    for index, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(index)
            return
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


# Точка входа для запуска приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)