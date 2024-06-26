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

# File import
from api.model import db, Pros, Options, Subscriptions, Clinics, Specializations, ClinicServices, HubAvailabilities, Hubs, Bookings, Patients, Provinces, ClinicInactivity, HubInactivity, HubServices, PatientForm, Surgeries, Allergies, Medications, Diseases
from api.services.email_utility import send_recovery_email, existing_pro_invitation_email, non_existing_pro_invitation_email, non_existing_owner_petition_email, existing_owner_petition_email, send_set_password_email, booking_confirmation_email
from api.services.auth_utility import set_new_password, verify_reset_token, generate_reset_token, register_pro, user_login
from api.services.invitations_utility import create_hub_from_invitation
from api.services.booking_availabilities_utility import get_date_range, get_hubs_by_clinic_service,get_availabilities_calendar, remove_availabilities_by_clinic_inactivity, remove_availabilities_by_hub_inactivity, remove_availabilities_by_booking, divide_availabilities_by_service_duration, consolidate_availabilities
from api.services.new_bookings_utility import create_new_patient, create_new_booking, update_patient, create_new_booking_from_pro
from api.services.date_utility import get_current_date
from api.services.patient_form_utility import create_new_allergies, create_new_medications, create_new_surgeries, create_new_diseases, update_patient_form
from api.services.options_utility import create_default_options

# blueprint setting
api = Blueprint('api', __name__)

@api.route('/')
def main():
    return 'this is the back running'

@api.route('/home')
def home():
    return 'HOME / this is the back running'




###################################################
## AUTHENTICATION


@api.route('/new-password', methods=['PUT'])
def new_password_setting():
    token = request.headers.get('Authorization')
    print('token in the link', token)
    return set_new_password(token)

@api.route('/verify-reset-token', methods=['POST']) # Used in the 'password setting page': if not valid, no acces to the page
def verify_reset_token_endpoint():
    token = request.json.get('token')
    return verify_reset_token(token)
 
@api.route('/reset-email', methods=['POST'])
def send_token_reset_email():
    email = request.json.get('email')
    token, message = generate_reset_token(email)

    if token:
        send_recovery_email(email, token)
        return jsonify({'message': message}), 200
    
    else:
        return jsonify({'message': message}),400

@api.route("/login", methods=['POST'])
def login():
    email = request.json.get("email")
    password = request.json.get("password")
    return user_login(email, password)

@api.route("/authentication", methods=["GET"])
@jwt_required()
def pro_authentication():  
    identity = get_jwt_identity()
    email = identity.get('email')
    if email:
        pro = Pros.query.filter_by(email=email).first()
        if pro:
            return jsonify(pro.serialize())
    
    return jsonify({"message": "Pro not found"}), 404



######################################################
# Provinces

# Get all provinces or post a new one
@api.route("/provinces", methods=['POST', "GET"])
def handle_provinces():
    if request.method == "POST":
        data = request.json
        required_fields = ['name', 'country', 'timeZone']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Incomplete data. Please provide all field informations"}), 400
        new_province = Provinces(
            country=data["country"],
            name=data['name'],
            time_zone=data['timeZone'])
        db.session.add(new_province)
        db.session.commit()
        return jsonify({"message": "Record added successfully", "province": new_province.serialize()}), 201
    if request.method == 'GET':
        provinces_list = Provinces.query.all()
        provinces = [provinces.serialize() for provinces in provinces_list]
        if not provinces_list:
            return jsonify({"message": "No province found in the table"}), 400
        else:
            return jsonify({"message": "Province list created", "data": provinces}), 200
        
















