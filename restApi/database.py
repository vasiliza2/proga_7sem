from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

# Константы (согласно PEP 8 пишутся в верхнем регистре)
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"

# Создание движка базы данных
# check_same_thread: False нужен только для SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Базовый класс для моделей (современный стиль SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass


# Модель таблицы Book
class BookDB(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    isbn = Column(String(13), nullable=True)


# Создание таблиц в базе данных
def create_tables():
    Base.metadata.create_all(bind=engine)


# Функция-зависимость для получения сессии базы данных
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()