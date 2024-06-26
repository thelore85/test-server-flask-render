from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy

# file api import
from api.admin import setup_admin
from api.routes import api
from api.model import db
from api.config import Config

# App - initialization
app = Flask(__name__)
app.config.from_object(Config)
# app.config["SQLALCHEMY_DATABASE_URI"] = "DB_URL"

# # Initialize SQLAlchemy and defining a simple Book model
# db = SQLAlchemy(app)

# class Book(db.Model):
#     book_id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String)

# # Create database tables in the PostgreSQL database
# with app.app_context():
#     db.create_all()

#setting
app.register_blueprint(api, url_prefix='/api')
setup_admin(app)

# Interface
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
    with app.app_context():
        db.create_all()