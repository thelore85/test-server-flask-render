from flask import Blueprint
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time, date, UTC, timedelta
import random
import os
import re
from sqlalchemy import not_
from flask_socketio import emit

# blueprint setting
api = Blueprint('api', __name__)

@api.route('/')
def main():
    return 'this is the back running'

@api.route('/home')
def home():
    return 'HOME / this is the back running'