from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# file api import
from api.admin import setup_admin
from api.routes import api
from api.model import db
from api.config import Config

# App - server
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/api/*": {"origins": "https://app.plannermed.com"}})

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