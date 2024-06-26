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

@api.route('/login', methods=['GET', 'POST'])
def login():
    email = request.json.get("email") 
    password = request.json.get("password")
    # user_login(email, password)
    print(email, password)
    return 'login in calling'


# @api.route("/login", methods=['POST'])
# def login():
#     email = request.json.get("email")
#     password = request.json.get("password")
#     return user_login(email, password)

@api.route('/home')
def home():
    return 'HOME / this is the back running'


############################################################
# Hub Availabilities

# Get all records in the 'HubAvailabilities' or Post one record
@api.route("/hubavailabilities", methods=['GET', 'POST'])
def hub_availabilities():
    if request.method == 'GET':
        hub_availabilities_list = HubAvailabilities.query.all()
        serialized_hub_availabilities = [availability.serialize() for availability in hub_availabilities_list]
        return jsonify({"data": serialized_hub_availabilities, "message": "Hub availabilities list downloaded"}), 200
    if request.method == 'POST':
        data = request.json
        final_hub_availabilities = []
        for hub_availability in data:
            if 'working_day' not in hub_availability or 'hubId' not in hub_availability:
                return jsonify({"message": "all data are required"}), 400
            starting_hour = datetime.strptime(hub_availability.get('starting_hour'), '%H:%M').time()
            ending_hour = datetime.strptime(hub_availability.get('ending_hour'), '%H:%M').time()
            hub_id = hub_availability.get('hubId')
            working_day = hub_availability.get('working_day')
            def add_availability(day):
                existing_availability = HubAvailabilities.query.filter_by(
                    hub_id=hub_id,
                    working_day=day,
                    starting_hour=starting_hour,
                    ending_hour=ending_hour
                ).first()
                if not existing_availability:
                    new_hub_availability = HubAvailabilities(
                        working_day=day,
                        starting_hour=starting_hour,
                        ending_hour=ending_hour,
                        hub_id=hub_id
                    )
                    db.session.add(new_hub_availability)
                    db.session.commit()
                    final_hub_availabilities.append(new_hub_availability.serialize())
            if working_day == 8:
                print('hey this is 8 :)')
                for i in range(1, 6):
                    add_availability(i)
            elif working_day == 9:
                for i in range(0, 7):
                    add_availability(i)
            else:
                add_availability(working_day)
        return jsonify({"message": "Record added successfully", "data": final_hub_availabilities}), 201  
    

# Get and delete all records in the 'HubAvailabilities' table by 'hub_id'
@api.route("/hubs/<int:hubid>/hubavailabilities", methods=['GET', 'DELETE'])
def specific_hub_hour(hubid):
    availabilities_by_hub = HubAvailabilities.query.filter_by(hub_id=hubid).all()
    if not availabilities_by_hub:
        return jsonify({"message": "Record not found"}), 404
    if request.method == 'GET':
        serialized_availabilities = [availability.serialize() for availability in availabilities_by_hub]
        return jsonify({"data": serialized_availabilities, "message": "Hub availabilities list for selected hub downloaded"}), 200
    if request.method == 'DELETE':
        availabilities_to_delete = HubAvailabilities.query.filter_by(hub_id=hubid).all()
        for availability in availabilities_to_delete:
            db.session.delete(availability)
        db.session.commit()
        return jsonify({"message": "Hub Availabilities deleted"}), 200
    
# Get, Update, and Delete a specific record in the 'HubAvailabilities' table
@api.route("/hubavailabilities/<int:hubavailabilityid>", methods=['GET', 'PUT', 'DELETE'])
def specific_hub_availability(hubavailabilityid):
    hub_availability = HubAvailabilities.query.get(hubavailabilityid)
    if not hub_availability:
        return jsonify({"message": "Record not found"}), 404
    if request.method == 'GET':
        return jsonify({"data": hub_availability.serialize(), "message": "Selected hub availability downloaded"}), 200
    if request.method == 'PUT':
        data = request.json
        hub_availability.working_day = data.get('workingDay', hub_availability.working_day)
        hub_availability.starting_hour = datetime.strptime(data['startingHour'], '%H:%M').time() if 'startingHour' in data else hub_availability.starting_hour
        hub_availability.ending_hour = datetime.strptime(data['endingHour'], '%H:%M').time() if 'endingHour' in data else hub_availability.ending_hour
        hub_availability.hub_id = data.get('hubId', hub_availability.hub_id)
        db.session.commit()
        return jsonify({"message": "Record updated successfully"}), 200
    if request.method == 'DELETE':
        db.session.delete(hub_availability)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully"}), 200




################################################################
# Specializations and clinicservices

# Get all clinicservices or post a new one.
@api.route("/clinicservices", methods=["GET", "POST"])
def handle_clinic_services():
    if request.method == 'GET':
        clinicservices_list = ClinicServices.query.all()
        serialized_clinicservices = [clinicservice.serialize() for clinicservice in clinicservices_list]
        return jsonify({"data": serialized_clinicservices, "message": "clinic services list downloaded"}), 200
    if request.method == 'POST':
        data = request.json
        final_clinicservices = []
        for clinicservice in data:
        # Check if the required fields are present in the request
            if 'clinicId' not in clinicservice or 'specializationId' not in clinicservice:
                return jsonify({"message": "clinicId and specializationId are required"}), 400
            new_clinicservice = ClinicServices(clinic_id=clinicservice['clinicId'],
                                        specialization_id=clinicservice['specializationId'],
                                        service_name=clinicservice.get('serviceName'),
                                        duration=clinicservice['duration'],
                                        price=clinicservice.get('price'),
                                        activated=clinicservice.get('activated'))
            db.session.add(new_clinicservice)
            db.session.commit()
            final_clinicservices.append(new_clinicservice.serialize())
        return jsonify({"message": "Records added successfully", "data": final_clinicservices}), 201

# Get, update or delete a specific clinicservice
@api.route("/clinicservices/<int:clinicserviceid>", methods=["GET", "PUT", "DELETE"])
def handle_clinicservice(clinicserviceid):
    clinic_service = ClinicServices.query.get(clinicserviceid)
    if not clinic_service:
        return jsonify({"message": "clinic service not found"}), 404
    if request.method == 'GET':
        return jsonify({"data": clinic_service.serialize(), "message": "Selected clinic service downloaded"}), 200
    if request.method == 'PUT':
        data = request.json
        clinic_service.price = data.get('price', clinic_service.price)
        clinic_service.clinic_id = data.get('clinicId', clinic_service.clinic_id)
        clinic_service.specialization_id = data.get('specializationId', clinic_service.specialization_id)
        clinic_service.duration = data.get('duration', clinic_service.duration)
        clinic_service.activated = data.get('activated', clinic_service.activated)
        clinic_service.service_name = data.get('serviceName', clinic_service.service_name)
        db.session.commit()
        if clinic_service.activated is False:
            hub_services_to_deactivate = HubServices.query.filter_by(clinic_service_id=clinic_service.id).all()
            for service in hub_services_to_deactivate:
                service.activated = False
            db.session.commit()
        return jsonify({"message": "clinic service updated successfully"}), 200
    if request.method == 'DELETE':
        db.session.delete(clinic_service)
        db.session.commit()
        return jsonify({"message": "clinic service deleted successfully"}), 200


# Get and Delete all clinicservices by clinic_id
@api.route("/clinics/<int:clinicid>/clinicservices", methods=["GET", "DELETE"])
def handle_clinicservices_by_clinic(clinicid):
    clinicservices_by_clinic = ClinicServices.query.filter_by(clinic_id=clinicid).all()
    if not clinicservices_by_clinic:
        return jsonify({"message": "No records found for the specified clinic_id"}), 404
    if request.method == 'GET':
        serialized_clinicservices = [clinicservice.serialize() for clinicservice in clinicservices_by_clinic]
        return jsonify({"data": serialized_clinicservices, "message": "Clinic Service list for selected clinic downloaded"}), 200
    if request.method == 'DELETE':
        for clinic_service in clinicservices_by_clinic:
            db.session.delete(clinic_service)
        db.session.commit()
        return jsonify({"message": "clinic services deleted successfully"}), 200


# Get all Specializations and Post new Specialization.
@api.route("/specializations", methods=["GET", "POST"])
def handle_services():
    if request.method == 'GET':
        specializations_list = Specializations.query.all()
        serialized_specializations = [specialization.serialize() for specialization in specializations_list]
        return jsonify({"data": serialized_specializations, "message": "Specializations list downloaded"}), 200
    if request.method == 'POST':
        data = request.json
        # Check if the required fields are present in the request
        if 'specialization' not in data:
            return jsonify({"message": "specialization is required"}), 400
        new_specialization = Specializations(specialization=data['specialization'])
        db.session.add(new_specialization)
        db.session.commit()
        return jsonify({"message": "Record added successfully", "data": new_specialization.serialize()}), 201



###################################################
## PRO

# Get Pro by username
@api.route("/pros/<string:username>", methods=["GET"])
def get_pro_by_username(username):
    pro = Pros.query.filter_by(username=username).first()
    if pro:
        return jsonify({"pro": pro.serialize()}), 200
    else:
        return jsonify({"message": "Pro not found"}), 404


# Create a new pro and get all pros
@api.route("/pros", methods=['POST', "GET"])
def signup_pro():
    if request.method == "POST":
        username = request.json.get("username", None) 
        email = request.json.get("email", None) 
        password = request.json.get("password", None)
        config_status = request.json.get("configStatus", None)
        terms_conditions = request.json.get("termsConditions", False)
        privacy_policy = request.json.get("privacyPolicy", False)
        marketing_consent = request.json.get("marketingConsent", False)
        success, message = register_pro(username, email, password, config_status, terms_conditions, privacy_policy, marketing_consent)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"message": message}), 401
    if request.method == 'GET':
        pros_list = Pros.query.all()
        serialized_pros = [pro.serialize() for pro in pros_list]
        if not pros_list:  
            return jsonify({"message": "No pros found", "error": "No pros available"}), 400
        else:
            return jsonify({"data": serialized_pros, "message": "Pro list downloaded"}), 200


# Get, update or delete a specific Pro.
@api.route("/pros/<int:proid>", methods=["GET", "PUT", "DELETE"])
def handle_pro(proid):
    pro = Pros.query.get(proid)
    if not pro:
        return jsonify({"message": "pro not found"}), 404
    if request.method == 'GET':
        return jsonify({"data": pro.serialize(), "message": "Selected Pro downloaded"}), 200
    if request.method == 'PUT':
        data = request.json
        print(data)
        # verify data has not empty value
        if not all(str(value).strip() for value in data.values()):
            return jsonify({"message": "Empty strings are not allowed"}), 400
        pro.name = data.get('name', pro.name)
        pro.lastname = data.get('lastname', pro.lastname)
        pro.email = data.get('email', pro.email)
        pro.phone = data.get('phone', pro.phone)
        pro.password = data.get('password', pro.password)
        pro.username = data.get('username', pro.username)
        pro.subscription_name = data.get('subscriptionName', pro.subscription_name)
        pro.config_status = data.get('configStatus', pro.config_status)
        pro.title = data.get('title', pro.title)
        pro.terms_conditions = data.get('termsConditions', pro.terms_conditions)
        pro.privacy_policy = data.get('privacyPolicy', pro.privacy_policy)
        pro.marketing_consent = data.get('marketingConsent', pro.marketing_consent)
        pro.creation_date = data.get('creationDate', pro.creation_date)
        pro.options_id = data.get('optionsId', pro.options_id)
        db.session.commit()
        return jsonify({"message": "Pro updated"}), 200
    if request.method == 'DELETE':
        db.session.delete(pro)
        db.session.commit()
        return jsonify({"message": "pro deleted successfully"}), 200
    
# Get Pro by calendar_page_url
@api.route('pros/url/<string:url>', methods=['GET'])
def get_pro_by_url(url):
    pro = Pros.query.join(Options).filter_by(calendar_page_url=url).first()
    if not pro:
        return jsonify({'error': f'Not pro found for the requested calendar page url {url}'}), 404
    return jsonify({'message': f'Pro downloaded for requested url {url}', 'data': pro.serialize()}), 200
    


################################################################
# CLINICS

# Get all records and add a new record to the 'clinics' table
@api.route("/clinics", methods=['GET', 'POST'])
def get_add_clinics():
    if request.method == 'GET':
        clinics_list = Clinics.query.all()
        serialized_clinics = [clinic.serialize() for clinic in clinics_list]
        if not clinics_list:  # Se la lista delle cliniche è vuota
            return jsonify({"message": "No clinics found", "error": "No clinics available"}), 400
        else:
            return jsonify({"data": serialized_clinics, "message": "Clinic list downloaded"}), 200
    if request.method == 'POST':
        data = request.json
        print(data)
        # Check if the required fields are present in the request
        required_fields = ['city', 'address', 'name', 'ownerId', "provinceId", "postalCode"]
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Incomplete data. Please provide all field informations"}), 400
        new_location = Clinics(
            owner_id=data["ownerId"],
            name=data['name'],
            city=data['city'],
            address=data['address'],
            postal_code=data['postalCode'],
            province_id=data['provinceId'],
            online_booking=data['onlineBooking'],
            color = data.get('color'),
            status = 'active',
            creation_date = datetime.now(UTC))
        db.session.add(new_location)
        db.session.commit()
        return jsonify({"message": "Record added successfully", "data": new_location.serialize()}), 201


# Get, Update, and Delete a specific record in the 'clinics' table
@api.route("/clinics/<int:clinicid>", methods=['GET', 'PUT', 'DELETE'])
def specific_clinic(clinicid):
    clinic = Clinics.query.get(clinicid)
    if not clinic:
        return jsonify({"message": "Record not found"}), 404
    if request.method == 'GET':
        return jsonify({"data":clinic.serialize(), "message":"Selected clinic downloaded"}), 200
    if request.method == 'PUT':
        data = request.json
        print(data)
        # Your existing code for updating the location record
        clinic.owner_id = data.get('ownerId', clinic.owner_id)
        clinic.name = data.get('name', clinic.name)
        clinic.address = data.get('address', clinic.address)
        clinic.city = data.get('city', clinic.city)
        clinic.province_id = data.get('provinceId', clinic.province_id)
        clinic.online_booking = data.get('online_booking', clinic.online_booking)
        clinic.postal_code = data.get('postalCode', clinic.postal_code)
        clinic.color = data.get('color', clinic.color)
        clinic.creation_date = data.get('creationDate', clinic.creation_date)
        clinic.status = data.get('status', clinic.status)
        db.session.commit()
        return jsonify({"message": "Record updated successfully"}), 200
    if request.method == 'DELETE':
        db.session.delete(clinic)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully"}), 200


# Get full clinics by pro_id
@api.route("/pros/<int:proid>/clinics", methods=["GET"])
def clinics_by_pro_id(proid):
    owned_clinics_by_pro = Clinics.query.filter_by(owner_id=proid).all()
    if not owned_clinics_by_pro:
        return jsonify({"message": "No clinics found for the specified pro_id", "data": []}), 200
    owned_serialized_clinics = []
    for clinic in owned_clinics_by_pro:
        clinic_dict = clinic.serialize()
        if clinic_dict['status'] != 'archived':
            clinic_dict['hubs'] = []
            clinic_dict['clinic_services'] = []
            clinic_services = ClinicServices.query.filter_by(clinic_id=clinic.id).all()
            hubs = Hubs.query.filter_by(clinic_id=clinic.id).all()
            for clinic_service in clinic_services:
                clinic_dict['clinic_services'].append(clinic_service.serialize())
            for hub in hubs:
                hub_dict = hub.serialize()
                hub_dict.pop('clinic', None)
                hub_dict['availabilities'] = []
                hub_dict['services'] = []
                hub_availabilities = HubAvailabilities.query.filter_by(hub_id=hub.id).all()
                hub_services = HubServices.query.filter_by(hub_id=hub.id).all()
                for availability in hub_availabilities:
                    hub_dict['availabilities'].append(availability.serialize())
                for service in hub_services:
                    hub_dict['services'].append(service.serialize())
                clinic_dict['hubs'].append(hub_dict)
            owned_serialized_clinics.append(clinic_dict)
    return jsonify({"data": owned_serialized_clinics, "message": "Owned clinics downloaded"}), 200


######################################################
# HUBS

# Get all Hubs and Post a new one
@api.route("/hubs", methods=['GET', 'POST'])
def get_add_hubs():
    if request.method == 'GET':
        hubs_list = Hubs.query.all()
        serialized_hubs = [hub.serialize() for hub in hubs_list]
        if not hubs_list:  
            return jsonify({"message": "No hubs found", "error": "No hubs available"}), 400
        else:
            return jsonify({"data": serialized_hubs, "message": "hub list downloaded"}), 200
    if request.method == 'POST':
        data = request.json
        print(data)
        required_fields = ['clinicId', 'proId']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Incomplete data. Please provide all field informations"}), 400
        new_hub = Hubs(
            clinic_id=data["clinicId"],
            pro_id=data['proId'],
            role=data.get('role'),
            status=data.get('status'),
            creation_date=datetime.now(UTC))
        db.session.add(new_hub)
        db.session.commit()
        return jsonify({"message": "Record added successfully", "data": new_hub.serialize()}), 201
    
# Get, Update, and Delete a specific record in the 'hubs' table
@api.route("/hubs/<int:hubid>", methods=['GET', 'PUT', 'DELETE'])
def specific_hub(hubid):
    hub = Hubs.query.get(hubid)
    if not hub:
        return jsonify({"message": "Record not found"}), 404
    if request.method == 'GET':
        return jsonify({"data": hub.serialize(), "message":"Selected hub downloaded"}), 200
    if request.method == 'PUT':
        data = request.json
        hub.clinic_id = data.get('clinicId', hub.clinic_id)
        hub.pro_id = data.get('proId', hub.pro_id)
        hub.role = data.get('role', hub.role)
        hub.status = data.get('status', hub.status)
        hub.creation_date = data.get('creationDate', hub.creation_date)
        db.session.commit()
        return jsonify({"message": "Record updated successfully", "data":hub.serialize()}), 200
    if request.method == 'DELETE':
        db.session.delete(hub)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully"}), 200
    
# Get or delete all hubs by pro_id
@api.route("/pros/<int:proid>/hubs", methods=["GET", "DELETE"])
def hubs_by_pro_id(proid):
    hubs_by_pro = Hubs.query.filter_by(pro_id=proid).filter(Hubs.status != 'archived').all()
    owned_clinics_hubs = Hubs.query.join(Clinics).filter_by(owner_id=proid).filter(Hubs.pro_id != proid, Hubs.status != 'archived').all()
    hubs_by_pro.extend(owned_clinics_hubs)
    if not hubs_by_pro:
        return jsonify({"message": "No hubs found for the specified pro_id", "data": []}), 200
    if request.method == "GET":
        serialized_hubs = []
        for hub in hubs_by_pro:
            hub_dict = hub.serialize()
            if hub_dict.get('clinic') and hub_dict['clinic'].get('status') != 'archived':  
                hub_dict["availabilities"] = []
                hub_dict["services"] = []
                hub_availabilities = HubAvailabilities.query.filter_by(hub_id=hub.id).all()
                hub_services = HubServices.query.filter_by(hub_id=hub.id).all()
                for hub_availability in hub_availabilities:
                    hub_dict["availabilities"].append(hub_availability.serialize())
                for hub_service in hub_services:
                    hub_dict["services"].append(hub_service.serialize())
                serialized_hubs.append(hub_dict)
        return jsonify({"data": serialized_hubs, "message": "Hub list for selected pro downloaded"}), 200
    if request.method == "DELETE":
        for hub in hubs_by_pro:
            db.session.delete(hub)
        db.session.commit()
        return jsonify({"message": "All hubs for the selected pro deleted!"}), 200


# Get or delete all hubs by clinic_id
@api.route("/clinics/<int:clinicid>/hubs", methods=["GET", "DELETE"])
def hubs_by_clinic_id(clinicid):
    hubs_by_clinic = Hubs.query.filter_by(clinic_id=clinicid)
    if not hubs_by_clinic:
        return jsonify({"message": "No hubs found for the specified clinic_id"}), 404
    if request.method == "GET":
        serialized_hubs = []
        for hub in hubs_by_clinic:
            hub_dict = hub.serialize()
            hub_dict["availabilities"] = []
            hub_dict["services"] = []
            hub_availabilities = HubAvailabilities.query.filter_by(hub_id=hub.id).all()
            hub_services = HubServices.query.filter_by(hub_id=hub.id).all()
            for hub_availability in hub_availabilities:
                hub_dict["availabilities"].append(hub_availability.serialize())
            for hub_service in hub_services:
                hub_dict["services"].append(hub_service.serialize())
            serialized_hubs.append(hub_dict)
        return jsonify({"data": serialized_hubs, "message": "Hub list for selected clinic downloaded"}), 200
    if request.method == "DELETE":
        for hub in hubs_by_clinic:
            db.session.delete(hub)
        db.session.commit()
        return jsonify({"message": "All hubs for the selected clinic deleted!"}), 200


######################################################
# Hub Services

# Get all hubservices and Post new hubservice.
@api.route("/hubservices", methods=["GET", "POST"])
def handle_hubservices():
    if request.method == 'GET':
        hubservices_list = HubServices.query.all()
        serialized_hubservices = [hubservice.serialize() for hubservice in hubservices_list]
        return jsonify({"data": serialized_hubservices, "message": "hubservices list downloaded"}), 200
    if request.method == 'POST':
        data = request.json
        print(data)
        final_hubservices = []
        if 'clinicServiceId' not in data or 'hubId' not in data:
            return jsonify({"message": "clinicServiceId and hubId are required"}), 400
        try:
            final_hub_service = {}
            existing_service = HubServices.query.filter_by(hub_id=data['hubId'], clinic_service_id=data['clinicServiceId']).first()
            if existing_service:
                existing_service.activated = True
                db.session.commit()
                final_hub_service = existing_service.serialize()
            if not existing_service:
                new_hubservice = HubServices(
                                            clinic_service_id=data['clinicServiceId'],
                                            hub_id=data['hubId'],
                                            activated = True
                                            )
                db.session.add(new_hubservice)
                db.session.commit()
                final_hub_service = new_hubservice.serialize()
        except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"Error while updating hubservice: {str(e)}"}), 500
            
        final_hubservices.append(final_hub_service)
    return jsonify({"message": "Records added successfully", "data": final_hubservices}), 201
    
# Get, Put or Delete a specific hubservice
@api.route('/hubservices/<int:hubserviceid>', methods=['GET', 'PUT', 'DELETE'])
def handle_hubservice(hubserviceid):
    hubservice = HubServices.query.get(hubserviceid)
    if not hubservice:
        return jsonify({"message": "Hubservice not found"}), 404
    if request.method == 'GET':
        return jsonify({"message": "Hubservice downloaded", "data": hubservice.serialize()})
    if request.method == 'PUT':
        data = request.json
        hubservice.clinic_service_id = data.get('clinicServiceId', hubservice.clinic_service_id)
        hubservice.hub_id = data.get('hubId', hubservice.hub_id)
        hubservice.activated = data.get('activated', hubservice.activated)
        db.session.commit()
        return jsonify({'message': 'Record updated successfully', 'data': hubservice.serialize()}), 200
    if request.method == 'DELETE':
        db.session.delete(hubservice)
        db.session.commit()
        return jsonify({'message': 'Record deleted succesfully'}), 200
    
# Get hubservices by hub_id
@api.route("/hubs/<int:hubid>/hubservices", methods=['GET'])
def handle_hubservices_by_hub_id(hubid):
    hubservices_by_hub = HubServices.query.filter_by(hub_id=hubid).all()
    if not hubservices_by_hub:
        return jsonify({"message": "No hub services found for this hub"}), 404
    if hubservices_by_hub:
        return jsonify({"message": "Hub services list for selected hub downloaded", "data": [hubservice.serialize() for hubservice in hubservices_by_hub]}), 200    



###################################################
# INVITATIONS
        
# Invite Pro to work in your clinic // from clinic to pro
@api.route("/add_collaborator", methods=['POST'])
def handle_pro_invitation():
    data = request.json
    invited_pro_email = data.get('proEmail')
    clinic_id = data.get('clinicId')
    availabilities = data.get('availability')
    services = data.get('services')
    pro = Pros.query.filter_by(email=invited_pro_email).first()
    if invited_pro_email == "":
        return jsonify({"message": "invalid email"}), 400
    if not pro:
        try:
            final_username = ''
            splitted_email = re.split(r'[@.]', invited_pro_email)
            existing_username = Pros.query.filter_by(username=splitted_email[0]).first()
            if existing_username:
                final_username = splitted_email[0] + str(random.randint(1, 1000))
            else:
                final_username = splitted_email[0]
            new_pro = Pros(
                username = final_username,
                email = invited_pro_email,
                password = os.getenv('PASSWORD_KEY_1') + str(random.randint(100000, 10000000)) + os.getenv('PASSWORD_KEY_2'),
                name = final_username,
                lastname = "",
                subscription_name = 'free',
                config_status = 10,
                creation_date = datetime.now(UTC)
            )
            db.session.add(new_pro)
            db.session.commit()
            create_default_options(final_username, new_pro.id)
            token, message = generate_reset_token(invited_pro_email)
            if token:
                try:
                    send_set_password_email(invited_pro_email, token)
                except Exception as e:
                    db.session.delete(new_pro)
                    db.session.commit()
                    return jsonify({"message": f"Can't create hub: Email could not be sent: {e}"}), 500
                try:
                    role = 'guest'
                    status = 'pending'
                    response = create_hub_from_invitation(new_pro, clinic_id, availabilities, services, role, status)
                    return jsonify({"message": "Invitation email sent to pro. Hub created", "data": {"hub": response["final_hub"], "clinic": response["final_clinic"]}}), 200
                except Exception as e:
                    return jsonify({"message": f"Hub could not be created: {e}"}), 500
            else:
                return jsonify({'message': message}),400  
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Somenthing went wrong: {e}"}), 500
    if pro:
        clinic = Clinics.query.get(clinic_id)
        clinic_hubs = Hubs.query.filter_by(clinic_id=clinic.id).filter(Hubs.status != 'archived').all()
        if clinic_hubs:
            for clinic_hub in clinic_hubs:
                if clinic_hub.pro.email == invited_pro_email:
                    return jsonify({"message": "This pro has already a hub in your clinic"}), 409

        if clinic.owner_id == pro.id:
            try:
                role = 'owner'
                status = 'active'
                response = create_hub_from_invitation(pro, clinic_id, availabilities, services, role, status)
                return jsonify({"message": "Created hub for yourself.", "data": {"hub": response["final_hub"], "clinic": response["final_clinic"]}}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": f"Sorry, somenthing went wrong: {e}"}), 500
        else:
            try:
                role = 'guest'
                status = 'pending'
                try:
                    existing_pro_invitation_email(pro, clinic_id)
                except Exception as e:
                    return jsonify({"message": f"Email could not be sent: {e}"})
                response = create_hub_from_invitation(pro, clinic_id, availabilities, services, role, status)
                return jsonify({"message": "Invitation mail sent to pro. Created hub for pro", "data": {"hub": response["final_hub"], "clinic": response["final_clinic"]}}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": f"Sorry, somenthing went wrong: {e}"}), 417
        
# Ask clinic to work with them // from pro to clinic
@api.route("/pros/petitions", methods=['POST'])
def handle_collab_petition():
    data = request.json
    pro_id = data.get('proId')
    owner_email = data.get('ownerEmail')
    owner = Pros.query.filter_by(email=owner_email).first()
    petitioner = Pros.query.get(pro_id)
    if not owner:
        try:
            non_existing_owner_petition_email(owner_email, petitioner)
            return jsonify({"message": "Petition email sent"}), 200
        except:
            return jsonify({"message": "Email could not be sent"}), 417
    if owner:
        try:
            existing_owner_petition_email(owner, petitioner)
            return jsonify({"message": "Petition email sent"}), 200
        except:
            return jsonify({"message": "Email could not be sent"}), 417
        

###################################################
# CLINIC CALENDAR

# Get calnedar events by clinic
@api.route('/pro_calendar/<int:proid>', methods=['GET'])
def get_clinic_calendar(proid):
    pro_calendar = {
        "bookings": [],
        "hubInactivities": [],
        "clinicInactivities": [],
    }
    try:
        clinics_by_pro = Clinics.query.filter_by(owner_id=proid).all()
        clinics_ids = []
        for clinic in clinics_by_pro:
            clinics_ids.append(clinic.id)
            confirmed_bookings = Bookings.query.join(HubServices).join(Hubs).filter_by(clinic_id=clinic.id).filter(Bookings.status == 'confirmed').all()
            pro_calendar['bookings'].extend([booking.serialize() for booking in confirmed_bookings])
            clinic_inactivities = ClinicInactivity.query.filter_by(clinic_id=clinic.id).all()
            serialized_clinic_inactivities = [inactivity.serialize() for inactivity in clinic_inactivities]
            for inactivity in serialized_clinic_inactivities:
                inactivity['role'] = 'owner' 
            pro_calendar['clinicInactivities'].extend(serialized_clinic_inactivities)
            hub_inactivities = HubInactivity.query.join(Hubs).filter_by(clinic_id=clinic.id).all()
            pro_calendar['hubInactivities'].extend([inactivity.serialize() for inactivity in hub_inactivities])
            pending_bookings = Bookings.query.join(HubServices).join(Hubs).filter_by(clinic_id=clinic.id).filter(Bookings.status == 'pending').all()
            pro_calendar['bookings'].extend([booking.serialize() for booking in pending_bookings])
    except Exception as e:
            return jsonify({"error": f"Error while getting events of owned clinics: {str(e)}"}), 500
    
    try:
        hubs_by_pro = Hubs.query.filter_by(pro_id=proid).filter(not_(Hubs.clinic_id.in_(clinics_ids))).all()
        for hub in hubs_by_pro:
            confirmed_bookings = Bookings.query.join(HubServices).filter_by(hub_id=hub.id).filter(Bookings.status == 'confirmed').all()
            pro_calendar['bookings'].extend([booking.serialize() for booking in confirmed_bookings])
            hub_inactivities = HubInactivity.query.filter_by(hub_id=hub.id).all()
            pro_calendar['hubInactivities'].extend([inactivity.serialize() for inactivity in hub_inactivities])
            pending_bookings = Bookings.query.join(HubServices).filter_by(hub_id=hub.id).filter(Bookings.status == 'pending').all()
            pro_calendar['bookings'].extend([booking.serialize() for booking in pending_bookings])
            external_clinics_inactivities = ClinicInactivity.query.join(Clinics).join(Hubs).filter_by(id=hub.id).all()
            serialized_external_clinics_inactivities = [clinic_inactivity.serialize() for clinic_inactivity in external_clinics_inactivities]
            for inactivity in serialized_external_clinics_inactivities:
                inactivity['role'] = 'guest'
            pro_calendar['clinicInactivities'].extend(serialized_external_clinics_inactivities)
    except Exception as e:
            return jsonify({"error": f"Error while getting events of owned hubs: {str(e)}"}), 500

    return jsonify(pro_calendar)



        

###################################################
# BOOKING AVAILABILITIES

# Get booking availabilities by clinic
@api.route("/booking_availabilities/<int:clinicid>", methods=['GET'])
def handle_booking_availabilities(clinicid):
    current_date = get_current_date(clinicid)
    try:
        clinic_services = ClinicServices.query.filter_by(clinic_id=clinicid).all()
        hubs_by_clinic_service = get_hubs_by_clinic_service(clinic_services)
    except Exception as e:
        return jsonify({"error": f"Error while fetching clinic services: {str(e)}"}), 500
    
    try:
        empty_calendar = get_date_range(clinicid)
    except Exception as e:
        return jsonify({"error": f"Error while fetching date range: {str(e)}"}), 500
    
    try:
        availabilities_calendar = get_availabilities_calendar(empty_calendar, hubs_by_clinic_service)
    except Exception as e:
        return jsonify({"error": f"Error while fetching availability calendar: {str(e)}"}), 500
    
    try:
        clinic_inactivities = ClinicInactivity.query.filter_by(clinic_id=clinicid).filter(ClinicInactivity.ending_date >= current_date).all()
        serialized_inactivities_clinic = [inactivity_clinic.serialize() for inactivity_clinic in clinic_inactivities]
        for inactivity_clinic in serialized_inactivities_clinic:
            availabilities_calendar = remove_availabilities_by_clinic_inactivity(availabilities_calendar, inactivity_clinic)
    except Exception as e:
        return jsonify({"error": f"Error while updating the calendar by clinic inactivities: {str(e)}"}), 500
    
    try:
        hub_inactivities_by_clinic_id = HubInactivity.query.join(Hubs).filter(Hubs.clinic_id == clinicid).filter(HubInactivity.ending_date >= current_date).all()
        serialized_inactivities = [inactivity.serialize() for inactivity in hub_inactivities_by_clinic_id]
        for inactivity in serialized_inactivities:
            availabilities_calendar = remove_availabilities_by_hub_inactivity(availabilities_calendar, inactivity) 
    except Exception as e:
        return jsonify({"error": f"Error while updating the calendar by hub inactivities: {str(e)}"}), 500

    try:
        bookings_by_clinic_services = []
        for service in clinic_services:
            bookings_by_clinic_services.extend(Bookings.query.join(HubServices)
                .filter(HubServices.clinic_service_id == service.id)
                .filter(Bookings.date >= current_date)
                .all()
            )
        final_bookings = [booking.serialize() for booking in bookings_by_clinic_services]
        for booking in final_bookings:
            availabilities_calendar = remove_availabilities_by_booking(availabilities_calendar, booking)
    except Exception as e:
        return jsonify({"error": f"Error while updating the calendar by bookings: {str(e)}"}), 500
    
    try:
        hub_services_by_clinic = HubServices.query.join(ClinicServices).filter_by(clinic_id=clinicid).all()
        final_hub_services = [service.serialize() for service in hub_services_by_clinic]
        slotted_calendar = divide_availabilities_by_service_duration(availabilities_calendar, final_hub_services)
        booking_availabilities_calendar = consolidate_availabilities(slotted_calendar)
    except Exception as e:
        return jsonify({"error": f"Error while slotting the calendar: {str(e)}"}), 500
    
    for day in booking_availabilities_calendar:
        if day['date'] == (current_date + timedelta(days=1)).strftime('%Y-%m-%d'):
            hour_tomorrow = (current_date + timedelta(days=1)).strftime('%H:%M')
            for booking_availability in day['bookingAvailabilities']:
                availabilities_to_keep = []
                for availability in booking_availability['availabilities']:
                    if datetime.strptime(availability, '%H:%M').time() >= datetime.strptime(hour_tomorrow, '%H:%M').time():
                        availabilities_to_keep.append(availability)
                booking_availability['availabilities'] = availabilities_to_keep
        if day['date'] > (current_date + timedelta(days=1)).strftime('%Y-%m-%d'):
            break

    for day in booking_availabilities_calendar:
        availabilities_to_keep = []
        if day['date'] > (current_date + timedelta(days=1)).strftime('%Y-%m-%d'):
            break
        for availability in day['bookingAvailabilities']:
            if len(availability['availabilities']) > 0:
                availabilities_to_keep.append(availability)
        day['bookingAvailabilities'] = availabilities_to_keep
    
    
    return jsonify(booking_availabilities_calendar), 200


######################################################
## PATIENTS

#get all patients
@api.route('/patients', methods=['GET'])
def get_patients():
    patients = Patients.query.all()
    return jsonify([patient.serialize() for patient in patients])

#Get all patientes by pro and owned clinics
@api.route('/patients/<int:proid>', methods=['GET'])
def get_patients_by_pro(proid):
    patients_list = []
    try:
        owned_clinics = Clinics.query.filter_by(owner_id=proid).all()
        for clinic in owned_clinics:
            clinic_patients = Patients.query.join(Bookings).join(HubServices).join(Hubs).filter_by(clinic_id=clinic.id).all()
            patients_list.extend([patient.serialize() for patient in clinic_patients])
    except Exception as e:
        return jsonify({"error": f"Error while getting patients of owned clinics: {str(e)}"}), 500
    
    try:
        pro_patients = Patients.query.join(Bookings).join(HubServices).join(Hubs).filter_by(pro_id=proid).all()
        patients_list.extend([pro_patient.serialize() for pro_patient in pro_patients])
        
    except Exception as e:
        return jsonify({"error": f"Error while getting patients by pro id: {str(e)}"}), 500
    
    unique_patients = {patient['id']: patient for patient in patients_list}
    filtered_patients_list = list(unique_patients.values())

    return jsonify(filtered_patients_list)


###################################################
## HUB INACTIVITIES 

# Get all Hub Inactivities or post a new one
@api.route('/hub_inactivities', methods=['GET', 'POST'])
def handle_hub_inactivities():
    if request.method == 'GET':
        clinic_inactivites = HubInactivity.query.all()
        return jsonify({"message": "Inactivities downloaded", "data": [inactivity.serialize() for inactivity in clinic_inactivites]})
    if request.method == 'POST':
        data = request.json
        try:
            new_hub_inactivity = HubInactivity(
                title = data.get('title'),
                starting_date = datetime.strptime(data.get('starting_date'), '%Y-%m-%dT%H:%M'),
                ending_date = datetime.strptime(data.get('ending_date'), '%Y-%m-%dT%H:%M'),
                type = data.get('type'),
                hub_id = data.get('hub_id')
            )
            db.session.add(new_hub_inactivity)
            db.session.commit()
            return jsonify({"message": "Hub inactivity created", "data": new_hub_inactivity.serialize()})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while creating new hub inactivity: {str(e)}"}), 500

# Get, update or delete a single hub inactivity
@api.route('/hub_inactivities/<int:inactivityid>', methods=['GET', 'PUT', 'DELETE'])
def handle_hub_inactivity(inactivityid):
    hub_inactivity = HubInactivity.query.get(inactivityid)
    if not hub_inactivity:
        return jsonify({'error': 'Inactivity not found'}), 404
    if request.method == 'GET':
        return jsonify({'message': "Hub Inactivity downloaded", "data": hub_inactivity.serialize()}), 200
    if request.method == 'PUT':
        data = request.json
        try:
            hub_inactivity.title = data.get('title', hub_inactivity.title)
            hub_inactivity.starting_date = datetime.strptime(data['starting_date'], '%Y-%m-%dT%H:%M') if 'starting_date' in data else hub_inactivity.starting_date
            hub_inactivity.ending_date = datetime.strptime(data['ending_date'], '%Y-%m-%dT%H:%M') if 'ending_date' in data else hub_inactivity.ending_date
            hub_inactivity.type = data.get('type', hub_inactivity.type)
            hub_inactivity.hub_id = data.get('hub_id', hub_inactivity.hub_id)
            db.session.commit()
            return jsonify({"message": "Hub inactivity updated", "data": hub_inactivity.serialize()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while updating hub inactivity: {str(e)}"}), 500
    if request.method == 'DELETE':
        try:
            db.session.delete(hub_inactivity)
            db.session.commit()
            return jsonify({"message": "Hub Inactivity succesfully deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while deleting hub inactivity: {str(e)}"}), 500



###################################################
## CLINIC INACTIVITIES 

# Get all Clinic Inactivities or post a new one
@api.route('/clinic_inactivities', methods=['GET', 'POST'])
def handle_clinic_inactivities():
    if request.method == 'GET':
        clinic_inactivites = ClinicInactivity.query.all()
        return jsonify({"message": "Clinic Inactivities downloaded", "data": [inactivity.serialize() for inactivity in clinic_inactivites]})
    if request.method == 'POST':
        data = request.json
        try:
            new_clinic_inactivity = ClinicInactivity(
                title = data.get('title'),
                starting_date = datetime.strptime(data.get('starting_date'), '%Y-%m-%dT%H:%M'),
                ending_date = datetime.strptime(data.get('ending_date'), '%Y-%m-%dT%H:%M'),
                type = data.get('type'),
                clinic_id = data.get('clinic_id'),
            )
            db.session.add(new_clinic_inactivity)
            db.session.commit()
            return jsonify({"message": "Clinic inactivity created", "data": new_clinic_inactivity.serialize()})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while creating new clinic inactivity: {str(e)}"}), 500

# Get, update or delete a single clinic inactivity
@api.route('/clinic_inactivities/<int:inactivityid>', methods=['GET', 'PUT', 'DELETE'])
def handle_clinic_inactivity(inactivityid):
    clinic_inactivity = ClinicInactivity.query.get(inactivityid)
    if not clinic_inactivity:
        return jsonify({'error': 'Inactivity not found'}), 404
    if request.method == 'GET':
        return jsonify({'message': "Clinic Inactivity downloaded", "data": clinic_inactivity.serialize()}), 200
    if request.method == 'PUT':
        data = request.json
        try:
            clinic_inactivity.title = data.get('title', clinic_inactivity.title)
            clinic_inactivity.starting_date = datetime.strptime(data['starting_date'], '%Y-%m-%dT%H:%M') if 'starting_date' in data else clinic_inactivity.starting_date
            clinic_inactivity.ending_date = datetime.strptime(data['ending_date'], '%Y-%m-%dT%H:%M') if 'ending_date' in data else clinic_inactivity.ending_date
            clinic_inactivity.type = data.get('type', clinic_inactivity.type)
            clinic_inactivity.clinic_id = data.get('clinic_id', clinic_inactivity.clinic_id)
            db.session.commit()
            return jsonify({"message": "clinic inactivity updated", "data": clinic_inactivity.serialize()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while updating clinic inactivity: {str(e)}"}), 500
    if request.method == 'DELETE':
        try:
            db.session.delete(clinic_inactivity)
            db.session.commit()
            return jsonify({"message": "Clinic Inactivity succesfully deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while deleting clinic inactivity: {str(e)}"}), 500


###################################################
## PATIENT FORM

# Post a new patient form
@api.route('/patient_form', methods=['POST'])
def handle_patient_forms():
    data = request.json
    patient_id = data.get('patientId')
    date_of_birth = datetime.strptime(data.get('dateOfBirth'), '%Y-%m-%d')
    sex = data.get('sex')
    allergies = data.get('allergy')
    surgeries = data.get('surgery')
    medications = data.get('medication')
    diseases = data.get('disease')

    if 'patientId' not in data:
        return jsonify({"error": "Missing patientId in data"}), 417
    
    patient = Patients.query.get(patient_id)
    if patient.form != None:
        return jsonify({"error": "Patient already has a form"}), 500
    
    try:
        if allergies:
            new_allergies = create_new_allergies(allergies)
        if surgeries:
            new_surgeries = create_new_surgeries(surgeries)
        if medications:
            new_medications = create_new_medications(medications)
        if diseases:
            new_diseases = create_new_diseases(diseases)
        if new_allergies or new_surgeries or new_medications or new_diseases:
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"SQLAlchemy Error while creating new blocks: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error while creating new blocks: {str(e)}"}), 500

    try:
        new_form = PatientForm(
            birth_date = date_of_birth,
            sex = sex
        )
        db.session.add(new_form)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"SQLAlchemy Error while creating new form: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error while creating new form: {str(e)}"}), 500
    
    try:
        if new_allergies:
            new_form.allergies_id = new_allergies.id
            db.session.commit()
        if new_medications:
            new_form.medications_id = new_medications.id
            db.session.commit()
        if new_surgeries:
            new_form.surgeries_id = new_surgeries.id
            db.session.commit()
        if new_diseases:
            new_form.diseases_id = new_diseases.id
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"SQLAlchemy Error while appending blocks to the form: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error while appending blocks to the form: {str(e)}"}), 500
    
    try:
        patient.form_id = new_form.id
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"SQLAlchemy Error while appending form to patient: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error while appending form to patient: {str(e)}"}), 500
    
    return jsonify({"message": "Form created successfully!"}), 200

# Get, Put or Delete a specific Pacient Form
@api.route('/patient_form/<int:formid>', methods=['GET', 'PUT', 'DELETE'])
def handle_patient_form(formid):
    if request.method == 'GET':
        form = PatientForm.query.get(formid)
        if not form:
            return jsonify({'error': 'Patient form not found'}), 404
        return jsonify({'message': 'Patient form downloaded', 'data': form.serialize()}), 200
    if request.method == 'PUT':
        form = request.json
        updated_form = update_patient_form(form)
        return jsonify(updated_form)
    if request.method == 'DELETE':
        try:
            form = request.json
            allergies = form['allergies']
            former_allergies = Allergies.query.get(allergies['id'])
            db.session.delete(former_allergies)
            medications = form['medications']
            former_medications = Medications.query.get(medications['id'])
            db.session.delete(former_medications)
            surgeries = form['surgeries']
            former_surgeries = Surgeries.query.get(surgeries['id'])
            db.session.delete(former_surgeries)
            diseases = form['diseases']
            former_diseases = Diseases.query.get(diseases['id'])
            db.session.delete(former_diseases)
            former_form = PatientForm.query.get(form['id'])
            db.session.delete(former_form)
            db.session.commit()
            return jsonify({"message": "Patient form succesfully deleted!"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"SQLAlchemy Error while deleting patient form: {str(e)}"}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error while deleting patient form: {str(e)}"}), 500
        
   
##################################################
## OPTIONS

# Get, Put or Delete a specific option
@api.route('/options/<int:optionid>', methods=['GET', 'PUT', 'DELETE'])
def handle_option(optionid):
    option = Options.query.get(optionid)
    if not option:
        return jsonify({"error": "Record not found"}), 404
    if request.method == 'GET':
        return jsonify({"message": "Options downloaded", "data": option.serialize()}), 200
    if request.method == 'PUT':
        data = request.json
        option.google_access_token = data.get('googleAccessToken', option.google_access_token)
        option.google_access_expires = data.get('googleAccessExpires', option.google_access_expires)
        option.google_refresh_token = data.get('googleRefreshToken', option.google_refresh_token)
        option.calendar_page_url = data.get('calendarPageUrl', option.calendar_page_url)
        option.calendar_availability_limit = data.get('calendarAvailabilityLimit', option.calendar_availability_limit)
        option.patient_booking_limit = data.get('patientBookingLimit', option.patient_booking_limit)
        option.payment_online = data.get('paymentOnline', option.payment_online)
        option.payment_offline = data.get('paymentOffline', option.payment_offline)
        option.reminder_booking_email = data.get('reminderBookingEmail', option.reminder_booking_email)
        option.cancel_booking_email = data.get('cancelBookingEmail', option.cancel_booking_email)
        db.session.commit()
        return jsonify({'message': 'Options successfully updated', 'data': option.serialize()}), 200
    if request.method == 'DELETE':
        db.session.delete(option)
        db.session.commit()
        return jsonify({'message': 'Options deleted succesfully'}), 200

# Get options by pro id
@api.route('/options/pro/<int:proid>', methods=['GET'])
def handle_options_by_pro(proid):
    options = Options.query.join(Pros).filter_by(id=proid).first()
    if not options:
        return jsonify({'error': 'Options not found'}), 404
    return jsonify({'message': f'Options for Pro {proid} downloaded', 'data': options.serialize()}), 200


###################################################
## SUBSCRIPTIONS

# Get subscription by pro id
@api.route('subscriptions/pro/<int:proid>', methods=['GET'])
def handle_subscription_by_pro(proid):
    subscription = Subscriptions.query.join(Pros).filter_by(id=proid).first()
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    return jsonify({'message': f'Subscription for Pro {proid} downloaded', 'data': subscription.serialize()}), 200




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

# @api.route("/login", methods=['POST'])
# def login():
#     email = request.json.get("email")
#     password = request.json.get("password")
#     return user_login(email, password)

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
            return jsonify({"message": "Province list downloaded", "data": provinces}), 200
        
















