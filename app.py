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
        name = request.form["name"]
        birth_date = date.fromisoformat(request.form["birthdate"])
        date_of_death_value = request.form.get("date_of_death")
        date_of_death = (
            date.fromisoformat(date_of_death_value)
            if date_of_death_value
            else None
        )

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        db.session.add(author)
        db.session.commit()

        return render_template('add_author.html', success_message="Author successfully added!")
    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = db.session.scalars(select(Author)).all()

    if request.method == 'POST':
        author_id = int(request.form["author_id"])
        isbn = request.form["isbn"]
        title = request.form["title"]
        publication_year = int(request.form["publication_year"])

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
    app.run(host="0.0.0.0", port=5000, debug=True)
