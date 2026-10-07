from flask import Flask, render_template
from data_models import db, Author, Book
from pathlib import Path
app = Flask(__name__)


basedir = Path(__file__).resolve().parent
database_path = basedir / "data" / "library.sqlite"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

db.init_app(app)

# with app.app_context():
#     db.create_all()

@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
