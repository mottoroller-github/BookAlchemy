from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import delete, select

from data_models import db, Author, Book

app = Flask(__name__)
app.config["SECRET_KEY"] = "9f8a7c6b5d4e3f2a1b0c"

basedir = Path(__file__).resolve().parent
database_path = basedir / "data" / "library.sqlite"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "title")

    if sort not in ("title", "author"):
        sort = "title"

    statement = select(Book)

    if search:
        statement = statement.where(Book.title.ilike(f"%{search}%"))

    if sort == "author":
        statement = statement.join(Book.author).order_by(Author.name)
    else:
        statement = statement.order_by(Book.title)

    books = db.session.scalars(statement).all()

    return render_template("home.html", books=books, current_sort=sort, search=search)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get("name", "").strip()
        birthdate_value = request.form.get("birthdate", "").strip()
        date_of_death_value = request.form.get("date_of_death", "").strip()

        if not name:
            return render_template("add_author.html", error_message="Name is required.")
        if not birthdate_value:
            return render_template("add_author.html", error_message="Birth date is required.")

        try:
            birth_date = date.fromisoformat(birthdate_value)
        except ValueError:
            return render_template("add_author.html", error_message="Invalid birth date.")

        if birth_date > date.today():
            return render_template("add_author.html", error_message="Birth date cannot be in the future.")

        if date_of_death_value:
            try:
                date_of_death = date.fromisoformat(date_of_death_value)
            except ValueError:
                return render_template("add_author.html", error_message="Invalid date of death.")

            if date_of_death > date.today():
                return render_template("add_author.html", error_message="Date of death cannot be in the future.")
            if date_of_death < birth_date:
                return render_template("add_author.html", error_message="Date of death cannot be before birth date.")
        else:
            date_of_death = None

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        db.session.add(author)
        db.session.commit()

        return render_template('add_author.html', success_message="Author successfully added!")
    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = db.session.scalars(select(Author)).all()

    if request.method == 'POST':
        title = request.form.get("title", "").strip()
        isbn = request.form.get("isbn", "").strip()
        publication_year_value = request.form.get("publication_year", "").strip()
        author_id_value = request.form.get("author_id", "").strip()

        if not title:
            return render_template("add_book.html", authors=authors, error_message="Title is required.")
        if not isbn:
            return render_template("add_book.html", authors=authors, error_message="ISBN is required.")
        if not publication_year_value:
            return render_template("add_book.html", authors=authors, error_message="Publication year is required.")

        try:
            publication_year = int(publication_year_value)
        except ValueError:
            return render_template("add_book.html", authors=authors, error_message="Publication year must be a number.")

        if publication_year < 1:
            return render_template("add_book.html", authors=authors, error_message="Publication year must be greater than 0.")
        if publication_year > date.today().year:
            return render_template("add_book.html", authors=authors, error_message="Publication year cannot be in the future.")

        if not author_id_value:
            return render_template("add_book.html", authors=authors, error_message="Author is required.")

        try:
            author_id = int(author_id_value)
        except ValueError:
            return render_template("add_book.html", authors=authors, error_message="Invalid author.")

        author = db.session.get(Author, author_id)

        if author is None:
            return render_template("add_book.html", authors=authors, error_message="Selected author does not exist.")

        book = Book(author_id=author_id, isbn=isbn, title=title, publication_year=publication_year)

        db.session.add(book)
        db.session.commit()

        return render_template('add_book.html', authors=authors, success_message="Book successfully added!")
    return render_template('add_book.html', authors=authors)

@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        flash("Book not found.", "error")
        return redirect(url_for("index"))

    author = book.author

    db.session.delete(book)
    db.session.flush()

    if not author.books:
        db.session.delete(author)

    db.session.commit()

    flash(f'Book "{book.title}" was successfully deleted.', "success")

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
