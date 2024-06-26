from flask import Blueprint

# blueprint setting
api = Blueprint('api', __name__)

@api.route('/')
def main():
    return 'this is the back running'

@api.route('/home')
def home():
    return 'HOME / this is the back running'