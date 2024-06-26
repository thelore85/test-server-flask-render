
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Time

# initialize
db = SQLAlchemy()


class Pros(db.Model):
    __tablename__ = "pros"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    phone = db.Column(db.String(25))
    title = db.Column(db.String)
    password = db.Column(db.String(80), nullable=False)
    config_status = db.Column(db.Integer, nullable=False)
    terms_conditions = db.Column(db.Boolean)
    privacy_policy = db.Column(db.Boolean)
    marketing_consent = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime)
    last_payment = db.Column(db.Date)
    subscription_name = db.Column(db.ForeignKey('subscriptions.subscription_name'))
    options_id = db.Column(db.ForeignKey('options.id'))
    subscription = db.relationship('Subscriptions')
    options = db.relationship('Options')
    
    def serialize(self):
        serialized_subscription = self.subscription.serialize() if self.subscription else None
        serialized_options = self.options.serialize() if self.options else None
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "configStatus": self.config_status,
            "creationDate": self.creation_date.strftime('%Y-%m-%dT%H:%M:%S'),
            "subscription": serialized_subscription,
            "options": serialized_options
        }


    def __repr__(self):
        return f'PRO: Email: {self.email}, ID: {self.id}'
  

class Clinics(db.Model):
    __tablename__ = "clinics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.Integer)
    color = db.Column(db.String)
    status = db.Column(db.String)
    online_booking = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime)
    province_id = db.Column(db.ForeignKey("provinces.id"))
    owner_id = db.Column(db.ForeignKey("pros.id"), nullable=False)
    owner = db.relationship("Pros")
    province = db.relationship("Provinces")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "owner": self.owner.name + " " + self.owner.lastname,
            "owner_id": self.owner.id,
            "postal_code": self.postal_code,
            "province": self.province.name,
            "online_booking": self.online_booking,
            "province_id": self.province.id,
            "time_zone": self.province.time_zone,
            "country": self.province.country,
            "color": self.color,
            "creation_date": self.creation_date,
            "status": self.status
        }

    def __repr__(self):
        return f'<Clinics: {self.name}, {self.id}>'

    
class HubAvailabilities(db.Model):
    __tablename__ = "hub_availabilities"
    id = db.Column(db.Integer, primary_key=True)
    working_day = db.Column(db.Integer, nullable=False) 
    starting_hour = db.Column(db.Time, nullable=False)
    ending_hour = db.Column(db.Time, nullable=False)
    hub_id = db.Column(db.ForeignKey("hubs.id"), nullable=False)
    hub = db.relationship("Hubs")

    def serialize(self):
        return {"id": self.id,
                "working_day": self.working_day,
                "starting_hour": self.starting_hour.strftime('%H:%M'),
                "ending_hour": self.ending_hour.strftime('%H:%M'),
                "hub_id": self.hub_id,
                }
    
    def __repr__(self):
        return f'<Hub Availabilities: {self.working_day}, {self.starting_hour}, {self.ending_hour}>'
    
    
class Hubs(db.Model):
    __tablename__ = "hubs"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    role = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime)
    clinic_id = db.Column(db.ForeignKey("clinics.id"))
    pro_id = db.Column(db.ForeignKey("pros.id"))
    clinic = db.relationship("Clinics")
    pro = db.relationship("Pros")

    def serialize(self):
        clinic_info = {}
        if self.clinic:
            clinic_info = {
                "id": self.clinic_id,
                "owner": f"{self.clinic.owner.name} {self.clinic.owner.lastname}",
                "owner_email": self.clinic.owner.email,
                "owner_phone": self.clinic.owner.phone,
                "country": self.clinic.province.country,
                "name": self.clinic.name,
                "address": self.clinic.address,
                "city": self.clinic.city,
                "postal_code": self.clinic.postal_code,
                "color": self.clinic.color,
                "status": self.clinic.status
            }
        pro_info = {
            "name": f"{self.pro.name} {self.pro.lastname}",
            "id": self.pro.id,
            "email": self.pro.email,
            "phone": self.pro.phone
        }
        return {
            "id": self.id,
            "status": self.status,
            "role": self.role,
            "creation_date": self.creation_date,
            "clinic": clinic_info,
            "pro": pro_info
        }

    
    def __repr__(self):
        return f'<Hub: {self.id}, {self.clinic.name}, {self.pro.email}>'


class HubInactivity(db.Model):
    __tablename__ = "hub_inactivity"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    starting_date = db.Column(db.DateTime, nullable=False) # 
    ending_date = db.Column(db.DateTime)                      # 2024-04-10T23:59:59
    type = db.Column(db.String)
    hub_id = db.Column(db.ForeignKey("hubs.id"), nullable=False)
    hub = db.relationship("Hubs")

    def serialize(self):
        return {"id": self.id,
                "title": self.title,
                "starting_date": self.starting_date.strftime('%Y-%m-%dT%H:%M:%S'),
                "ending_date": self.ending_date.strftime('%Y-%m-%dT%H:%M:%S'),
                "type": self.type,
                "clinic_id": self.hub.clinic.id,
                "hub_id": self.hub_id,
                "role": self.hub.role,
                "clinic_name": self.hub.clinic.name,
                "pro_name": self.hub.pro.name + " " + self.hub.pro.lastname}
    
    def __repr__(self):
        return f'<Hub Inactivity: {self.title}>'


class Patients(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(25))
    creation_date = db.Column(db.DateTime)
    privacy_policy = db.Column(db.Boolean)
    marketing_policy = db.Column(db.Boolean)
    form_id = db.Column(db.ForeignKey("patient_form.id"))
    form = db.relationship("PatientForm")

    def __repr__(self):
        return f'<Patient {self.name}, {self.email}>'

    def serialize(self):
        patient_form = self.form.serialize() if self.form else None
        return {"id": self.id,
                "name": self.name,
                "email": self.email,
                "phone": self.phone,
                "creation_date": self.creation_date,
                "form": patient_form}


class Specializations(db.Model):
    __tablename__ = "specializations"
    id = db.Column(db.Integer, primary_key=True)
    specialization = db.Column(db.String, nullable=False)

    def serialize(self):
        return {"id": self.id,
                "specialization": self.specialization,
                }

    def __repr__(self):
        return f'<Specialization: {self.specialization}>'
    
    
class HubServices(db.Model):
    __tablename__ = "hub_services"   
    id = db.Column(db.Integer, primary_key=True)
    clinic_service_id = db.Column(db.ForeignKey("clinic_services.id"), nullable=False)
    activated = db.Column(db.Boolean)
    hub_id = db.Column(db.ForeignKey("hubs.id"), nullable=True)
    clinic_service = db.relationship("ClinicServices")
    hub = db.relationship("Hubs")

    def serialize(self):
        return {"id": self.id,
                "clinicServiceId": self.clinic_service_id,
                "hubId": self.hub_id,
                "specialization": self.clinic_service.specialization.specialization,
                "serviceName": self.clinic_service.service_name,
                "price": self.clinic_service.price,
                "duration": self.clinic_service.duration,
                "activated": self.activated
                }
    
    def __repr__(self):
        return f'Service Hub: {self.id}, {self.clinic_service}, {self.hub}.'

class ClinicServices(db.Model):
    __tablename__ = "clinic_services"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    clinic_id = db.Column(db.ForeignKey("clinics.id"), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer)
    service_name = db.Column(db.String, nullable=False)
    specialization_id = db.Column(db.ForeignKey("specializations.id"), nullable=False)
    activated = db.Column(db.Boolean)
    specialization = db.relationship("Specializations")
    clinic = db.relationship("Clinics")

    def serialize(self):
        return {"clinicId": self.clinic_id,
                "id": self.id,
                "specialization": self.specialization.specialization,
                "serviceName": self.service_name,
                "price": self.price,
                "duration": self.duration,
                "activated": self.activated
                }

    def __repr__(self):
        return f'<Clinic service: {self.specialization.specialization}, {self.service_name},  {self.price}, {self.duration} >'


class Bookings(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False) #2024-04-06T00:00:00
    status = db.Column(db.String, nullable=False)
    pro_notes = db.Column(db.String)
    patient_notes = db.Column(db.String)
    creation_date = db.Column(db.DateTime)
    expiration_date = db.Column(db.DateTime)
    reminder_sent = db.Column(db.Boolean)
    hub_service_id = db.Column(db.ForeignKey("hub_services.id"), nullable=False)
    patient_id = db.Column(db.ForeignKey("patients.id"), nullable=False)
    hub_service = db.relationship("HubServices")
    patient = db.relationship("Patients")

    def serialize(self):
        booking_start = self.date
        booking_duration = timedelta(minutes=self.hub_service.clinic_service.duration)
        booking_end = booking_start + booking_duration
        return {"id": self.id,
                "date": self.date.strftime('%Y-%m-%dT%H:%M'),
                "ending_date": booking_end.strftime('%Y-%m-%dT%H:%M'),
                "status": self.status,
                "patient_id": self.patient_id,
                "hub_service_id": self.hub_service_id,
                "patient_notes": self.patient_notes,
                "pro_notes": self.pro_notes,
                "duration": self.hub_service.clinic_service.duration,
                "hubId": self.hub_service.hub_id,
                "patient_name": self.patient.name,
                "patient_phone": self.patient.phone,
                "patient_email": self.patient.email,
                "specialization": self.hub_service.clinic_service.specialization.specialization,
                "specialization_id": self.hub_service.clinic_service.specialization.id,
                "service": self.hub_service.clinic_service.service_name,
                "clinic_id": self.hub_service.clinic_service.clinic.id,
                "clinic_service_id": self.hub_service.clinic_service.id,
                "clinic_name": self.hub_service.clinic_service.clinic.name,
                "clinic_address": self.hub_service.clinic_service.clinic.address,
                "clinic_city": self.hub_service.clinic_service.clinic.city,
                "clinic_province": self.hub_service.clinic_service.clinic.province.name,
                "clinic_country": self.hub_service.clinic_service.clinic.province.country,
                "doctor_name": self.hub_service.hub.pro.name + " " + self.hub_service.hub.pro.lastname,
                "doctor_email": self.hub_service.hub.pro.email,
                "doctor_role": self.hub_service.hub.role,
                "doctor_id": self.hub_service.hub.pro.id,
                "creation_date": self.creation_date.strftime('%Y-%m-%dT%H:%M')
                }

    def __repr__(self):
        return f'<Booking: id: {self.id}, date: {self.date}, patient: {self.patient.name} >'
    

class Provinces(db.Model):
    __tablename__ = "provinces"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    time_zone = db.Column(db.String)

    def serialize(self):
        return {"id": self.id,
                "name": self.name,
                "country": self.country,
                "time_zone": self.time_zone
                }

    def __repr__(self):
        return f'Province: {self.name}, {self.country}'
    

class ClinicInactivity(db.Model):
    __tablename__ = "clinic_inactivity"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    starting_date = db.Column(db.DateTime, nullable=False)
    ending_date = db.Column(db.DateTime)
    type = db.Column(db.String)
    clinic_id = db.Column(db.ForeignKey("clinics.id"), nullable=False)
    clinic = db.relationship("Clinics")

    def serialize(self):
        return {"id": self.id,
                "title": self.title,
                "starting_date": self.starting_date.strftime('%Y-%m-%dT%H:%M:%S'),
                "ending_date": self.ending_date.strftime('%Y-%m-%dT%H:%M:%S'),
                "type": self.type,
                "clinic_id": self.clinic_id,
                "clinic_name": self.clinic.name}
    
    def __repr__(self):
        return f'<Clinic Inactivity: {self.title}>'
    
class PatientForm(db.Model):
    __tablename__ = "patient_form"
    id = db.Column(db.Integer, primary_key=True)
    birth_date = db.Column(db.Date)
    sex = db.Column(db.String)
    allergies_id = db.Column(db.ForeignKey("allergies.id"))
    surgeries_id = db.Column(db.ForeignKey("surgeries.id"))
    medications_id = db.Column(db.ForeignKey("medications.id"))
    diseases_id = db.Column(db.ForeignKey("diseases.id"))
    allergies = db.relationship("Allergies")
    medications = db.relationship("Medications")
    surgeries = db.relationship("Surgeries")
    diseases = db.relationship("Diseases")

    def serialize(self):
        allergies_form = self.allergies.serialize() if self.allergies else None
        surgeries_form = self.surgeries.serialize() if self.surgeries else None
        medications_form = self.medications.serialize() if self.medications else None
        diseases_form = self.diseases.serialize() if self.diseases else None
        return {
            "id": self.id,
            "birthDate": self.birth_date.strftime('%Y-%m-%d'),
            "sex": self.sex,
            "allergies": allergies_form,
            "surgeries": surgeries_form,
            "medications": medications_form,
            "diseases": diseases_form,
        }
    
    def __repr__(self):
        return f'<Patient Form: {self.id}, {self.birth_date}, {self.sex}>'
    
    
class Allergies(db.Model):
    __tablename__ = "allergies"
    id = db.Column(db.Integer, primary_key=True)
    no_allergies = db.Column(db.Boolean)
    other = db.Column(db.Boolean)
    aspirin = db.Column(db.Boolean)
    penicillin = db.Column(db.Boolean)
    sulfa_drugs = db.Column(db.Boolean)
    nsaids = db.Column(db.Boolean)
    chemotherapy = db.Column(db.Boolean)

    def serialize(self):
        return {"id": self.id,
                "nothingToDeclare": self.no_allergies,
                "other": self.other,
                "aspirin": self.aspirin,
                "penicillin": self.penicillin,
                "sulfaDrugs": self.sulfa_drugs,
                "NSAIDs": self.nsaids,
                "chemotherapyDrugs": self.chemotherapy}
    
    def __repr__(self):
        return f'<Allergies: {self.id}>'
    
    
class Surgeries(db.Model):
    __tablename__ = "surgeries"
    id = db.Column(db.Integer, primary_key=True)
    no_surgeries = db.Column(db.Boolean)
    other = db.Column(db.Boolean)
    appendectomy = db.Column(db.Boolean)
    cholecystectomy = db.Column(db.Boolean)
    csection = db.Column(db.Boolean)
    mastectomy = db.Column(db.Boolean)

    def serialize(self):
        return {"id": self.id,
                "nothingToDeclare": self.no_surgeries,
                "other": self.other,
                "appendectomy": self.appendectomy,
                "cholecystectomy": self.cholecystectomy,
                "csection": self.csection,
                "mastectomy": self.mastectomy,
                }
    
    def __repr__(self):
        return f'<Surgeries: {self.id}>'
    
    
class Medications(db.Model):
    __tablename__ = "medications"
    id = db.Column(db.Integer, primary_key=True)
    no_medications = db.Column(db.Boolean)
    other = db.Column(db.Boolean)
    antihypertensives = db.Column(db.Boolean)
    statins = db.Column(db.Boolean)
    diabetes = db.Column(db.Boolean)
    thyroid = db.Column(db.Boolean)
    anticoagulants = db.Column(db.Boolean)

    def serialize(self):
        return {"id": self.id,
                "nothingToDeclare": self.no_medications,
                "other": self.other,
                "antihypertensives": self.antihypertensives,
                "statins": self.statins,
                "diabetesMedication": self.diabetes,
                "thyroidMedications": self.thyroid,
                "anticoagulants": self.anticoagulants
                }
    
    def __repr__(self):
        return f'<Medications: {self.id}>'
    
    
class Diseases(db.Model):
    __tablename__ = "diseases"
    id = db.Column(db.Integer, primary_key=True)
    no_diseases = db.Column(db.Boolean)
    other = db.Column(db.Boolean)
    hypertension = db.Column(db.Boolean)
    diabetes = db.Column(db.Boolean)
    heart_disease = db.Column(db.Boolean)
    copd = db.Column(db.Boolean)

    def serialize(self):
        return {"id": self.id,
                "nothingToDeclare": self.no_diseases,
                "other": self.other,
                "hypertension": self.hypertension,
                "diabetes": self.diabetes,
                "heartDisease": self.heart_disease,
                "copd": self.copd
                }
    
    def __repr__(self):
        return f'<Diseases: {self.id}>'
    
class Subscriptions(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    subscription_name = db.Column(db.String, unique=True)
    online_booking_function = db.Column(db.Boolean)
    online_payment_function = db.Column(db.Boolean)
    vacation_function = db.Column(db.Boolean)
    patient_manager_function = db.Column(db.Boolean)
    notification_center = db.Column(db.Boolean)
    clinic_number = db.Column(db.Integer)
    collaborator_number = db.Column(db.Integer)
    service_number = db.Column(db.Integer)
    days = db.Column(db.Integer)

    def serialize(self):
        return {
            'id': self.id,
            'subscriptionName': self.subscription_name,
            'onlineBookingFunction': self.online_booking_function,
            'onlinePaymentFunction': self.online_payment_function,
            'vacationFunction': self.vacation_function,
            'patientManagerFunction': self.patient_manager_function,
            'clinicNumber': self.clinic_number,
            'collaboratorNumber': self.collaborator_number,
            'serviceNumber': self.service_number,
            'days': self.days
        },

    def __repr__(self):
        return f'<Subscription: {self.subscription_name}>'
    

class Options(db.Model):
    __tablename__ = "options"
    id = db.Column(db.Integer, primary_key=True)
    google_access_token = db.Column(db.String)
    google_access_expires = db.Column(db.String)
    google_refresh_token = db.Column(db.String)
    calendar_page_url = db.Column(db.String(20), unique=True)
    calendar_availability_limit = db.Column(db.Integer)
    patient_booking_limit = db.Column(db.Boolean)
    payment_online = db.Column(db.Boolean)
    payment_offline = db.Column(db.Boolean)
    reminder_booking_email = db.Column(db.Boolean)
    cancel_booking_email = db.Column(db.Boolean)

    def serialize(self):
        return {
            'id': self.id,
            'googleAccessToken': self.google_access_token,
            'googleAccessExpires': self.google_access_expires,
            'googleRefreshToken': self.google_refresh_token,
            'calendarPageUrl': self.calendar_page_url,
            'calendarAvailabilityLimit': self.calendar_availability_limit,
            'patientBookingLimit': self.patient_booking_limit,
            'paymentOnline': self.payment_online,
            'paymentOffline': self.payment_offline,
            'reminderBookingEmail': self.reminder_booking_email,
            'cancelBookingEmail': self.cancel_booking_email
        }
    
    def __repr__(self):
        return f'Options id: {self.id}'


        


   
        




