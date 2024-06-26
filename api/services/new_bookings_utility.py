from api.model import Pros, Clinics, Hubs, HubAvailabilities, HubInactivity, HubServices, ClinicServices, Patients, Bookings, db
from datetime import datetime, time, date, UTC, timedelta

def create_new_patient(patient):
    new_patient = Patients(
        email = patient.get('email'),
        name = patient.get('name'),
        phone = patient.get('phone'),
        privacy_policy = patient.get('privacyPolicy'),
        marketing_policy = patient.get('marketingPolicy'),
        creation_date = datetime.now(UTC)
    )
    db.session.add(new_patient)
    db.session.commit()
    return(new_patient)

def update_patient(updated_patient, former_patient):
    former_patient.name = updated_patient.get('name')
    former_patient.email = updated_patient.get('email')
    former_patient.phone = updated_patient.get('phone')
    former_patient.privacy_policy = updated_patient.get('privacyPolicy')
    former_patient.marketing_policy = updated_patient.get('marketingPolicy')
    db.session.commit()



def create_new_booking(date, patient_notes, hub_service_id, patient_id):
    new_booking = Bookings(
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M'),
        patient_notes = patient_notes,
        hub_service_id = hub_service_id,
        patient_id = patient_id,
        status = "pending",
        creation_date = datetime.now(UTC),
        expiration_date = datetime.now(UTC) + timedelta(hours=1),
        reminder_sent = False
    )
    db.session.add(new_booking)
    db.session.commit()
    return(new_booking)

def create_new_booking_from_pro(booking, patient_id):
    new_booking = Bookings(
        date = datetime.strptime(booking['date'], '%Y-%m-%dT%H:%M'),
        pro_notes = booking['proNotes'],
        hub_service_id = booking['hubServiceId'],
        patient_id = patient_id,
        status = "confirmed",
        creation_date = datetime.now(UTC),
        reminder_sent = False
    )
    db.session.add(new_booking)
    db.session.commit()
    return(new_booking)