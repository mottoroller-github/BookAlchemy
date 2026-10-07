from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    birth_date: Mapped[date]
    date_of_death: Mapped[date | None]

    books: Mapped[list["Book"]] = relationship(back_populates="author")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Author id={self.id} name={self.name} birth_date={self.birth_date} date_of_death={self.date_of_death}>"


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    isbn: Mapped[str]
    title: Mapped[str]
    publication_year: Mapped[int]

    author: Mapped["Author"] = relationship(back_populates="books")

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f"<Book id={self.id} isbn={self.isbn} title='{self.title}' publication_year={self.publication_year}>"
