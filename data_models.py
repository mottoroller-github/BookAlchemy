"""Database models for authors and books in the library."""
from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Author(db.Model):
    """Represent an author in the library database."""
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)  # nullable=False is default
    birth_date: Mapped[date]
    date_of_death: Mapped[date | None]

    books: Mapped[list["Book"]] = relationship(back_populates="author")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (f"<Author id={self.id} "
                f"name={self.name} "
                f"birth_date={self.birth_date} "
                f"date_of_death={self.date_of_death}>")


class Book(db.Model):
    """Represent a book in the library database."""
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    isbn: Mapped[str] = mapped_column(unique=True)  # nullable=False is default
    title: Mapped[str]
    publication_year: Mapped[int]

    author: Mapped["Author"] = relationship(back_populates="books")

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (f"<Book id={self.id} "
                f"isbn={self.isbn} "
                f"title='{self.title}' "
                f"publication_year={self.publication_year}>")
