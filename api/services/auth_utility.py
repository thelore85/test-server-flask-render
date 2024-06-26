from flask import jsonify, request
from flask_jwt_extended import create_access_token
from datetime import datetime, UTC


import jwt
import os
from api.model import db, Pros
import bcrypt
from time import time
from api.services.options_utility import create_default_options



#LOGIN
def user_login(email, password):
    pro = Pros.query.filter_by(email=email).first()

    if pro and bcrypt.checkpw(password.encode('utf-8'), pro.password):
        identity = {
            "id": pro.id,
            "username": pro.username,
            "email": pro.email,
        }
        token = create_access_token(identity=identity)
        return jsonify(access_token=token, message="user logged in successfully"), 200
    
    return jsonify(message="User not found: invalid Email or Password"), 404



# SIGNUP: New User creation
def register_pro(username, email, password, config_status, terms_conditions, privacy_policy, marketing_consent):
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    existing_pro_email = Pros.query.filter_by(email=email).first()
    existing_pro_username = Pros.query.filter_by(username=username).first()

    if existing_pro_email or existing_pro_username:
        return False, "User already exists"


    if not (email.strip() and password.strip() and username.strip() and config_status is not None):
        return False, "Invalid Email, Password, or Username"


    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    new_pro = Pros(username=username, email=email, password=hashed_password, config_status=config_status, privacy_policy=privacy_policy, terms_conditions=terms_conditions, marketing_consent=marketing_consent, creation_date=datetime.now(UTC))
    db.session.add(new_pro)
    try:
        db.session.commit()
        create_default_options(username, new_pro.id)
    except Exception as e:
        db.session.rollback()
        return False, f"Error while creating default options: {str(e)}"

    return True, "User registered successfully"



# PSW TOKEN: Generate reset token
def generate_reset_token(user_email):
    expires=500
    secret_key = os.getenv('SECRET_KEY_FLASK')
    if secret_key is None:
        raise ValueError("SECRET_KEY_FLASK not set correctly")
    
    user = Pros.query.filter_by(email = user_email).first()
    if user is None:
        return False, "No user with this email"
    
    if user:
        token = jwt.encode({'email': user.email, 'reset_password': user.username, 'exp': time() + expires}, key=secret_key)
        return token, "Token Generated"



# PSW TOKEN CHECK: Check if reset toke is still valid and if match en existing user 
def verify_reset_token(token):
    print(token)
    
    if not token:
        return jsonify({"message": "Missing Token"}), 400

    try:
        payload = jwt.decode(token, key=os.getenv('SECRET_KEY_FLASK'), algorithms=["HS256"])
        pro_email = payload.get('email')
        pro = Pros.query.filter_by(email=pro_email).first()

        print('pro verify token', pro.serialize())
        if pro:
            return jsonify({"user": pro.serialize(), "message": "Token correct, User identified"}), 200
        else:
            return jsonify({"message": "User not found"}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token invalid"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500



# UPDATE PSW: Update psw in the user table record
def set_new_password(token):
    if not token:
        return jsonify({"message": "Missing Token"}), 400
    
    token = token.split()[1]

    try:
        payload = jwt.decode(token, key=os.getenv('SECRET_KEY_FLASK'), algorithms=["HS256"])
        pro_email = payload.get('email')

        email = request.json.get('email')
        new_password = request.json.get('password')
        new_password_bytes = new_password.encode('utf-8') if new_password is not None else None # Convert string to byte string

        if pro_email != email:
            return jsonify({"message": "Email in the token don't match email provided"}), 400

        Pro = Pros.query.filter_by(email=email).first()
        if Pro:
            hashed_password = bcrypt.hashpw(new_password_bytes, bcrypt.gensalt())
            Pro.password = hashed_password
            db.session.commit()
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({"message": 'Pro not found'}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token invalid"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    


