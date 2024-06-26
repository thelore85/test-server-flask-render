from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# from flask_cors import CORS
# from flask_socketio import SocketIO


# file api import
from api.admin import setup_admin
from api.routes import api
# from api.model import db
# from api.config import Config


# App initialization
app = Flask(__name__)


#setting
app.register_blueprint(api, url_prefix='/api')
# app.config.from_object(Config)    
setup_admin(app)
# CORS(app)


# Interface
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
    # with app.app_context():
        # db.create_all()