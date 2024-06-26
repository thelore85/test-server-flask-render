import os
from api.model import db, Pros, Clinics, HubAvailabilities, Options, Subscriptions, Provinces, HubInactivity, Patients, Specializations, ClinicServices, Bookings, Hubs, ClinicInactivity, HubServices, PatientForm, Allergies, Surgeries, Medications, Diseases
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
    admin = Admin(app, name='Admin panel', template_mode='bootstrap4')


    class ProsAdminView(ModelView):
        column_display_pk = True 
        form_columns = ['email', 'username', 'name', 'lastname', 'phone', 'subscription_name', 'title', 'password', 'config_status', 'privacy_policy', 'marketing_consent', 'last_payment', 'creation_date', 'options_id']

    class ClinicsAdminView(ModelView):
        column_display_pk = True
        form_columns = ['name', 'address', 'city', 'online_booking', 'postal_code', 'province', 'owner', 'status', 'creation_date']

    class HubAvailabilitiesAdminView(ModelView):
        column_display_pk = True
        form_columns = ['hub', 'working_day', 'starting_hour', 'ending_hour']

    class HubsAdminView(ModelView):
        column_display_pk = True
        form_columns = ['clinic', 'pro', 'status', 'role']

    class HubInactivityAdminView(ModelView):
        column_display_pk = True
        form_columns = ['title', 'starting_date', 'ending_date', 'type', 'hub']

    class PatientsAdminView(ModelView):
        column_display_pk = True
        form_columns = ['name', 'email', 'phone', 'privacy_policy', 'marketing_policy', 'creation_date']

    class SpecializationsAdminView(ModelView):
        column_display_pk = True
        form_columns = ['specialization']

    class ClinicServicesAdminView(ModelView):
        column_display_pk = True
        form_columns = ['clinic', 'price', 'duration', 'service_name', 'specialization', 'activated']

    class BookingsAdminView(ModelView):
        column_display_pk = True
        form_columns = ['date', 'status', 'pro_notes', 'patient_notes', 'hub_service', 'patient', 'creation_date', 'expiration_date']

    class ProvincesAdminView(ModelView):
        column_display_pk = True
        form_columns = ['name', 'country', 'time_zone']

    class ClinicInactivityAdminView(ModelView):
        column_display_pk = True
        form_columns = ['title', 'starting_date', 'ending_date', 'type', 'clinic']

    class HubServicesAdminView(ModelView):
        column_display_pk = True
        form_columns = ['clinic_service_id', 'hub_id', 'activated']

    class PatientFormAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'birth_date', 'sex', 'allergies_id', 
            'surgeries_id', 'medications_id'
        ]

    class AllergiesAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'no_allergies', 'other', 'aspirin', 
            'penicillin', 'sulfa_drugs', 'nsaids', 
            'chemotherapy'
        ]

    class SurgeriesAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'no_surgeries', 'other', 'appendectomy', 
            'cholecystectomy', 'csection', 'mastectomy'
        ]

    class MedicationsAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'no_medications', 'other', 'antihypertensives', 
            'statins', 'diabetes', 'thyroid', 'anticoagulants'
        ]
    class DiseasesAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'no_diseases', 'other', 'hypertension', 
            'heart_disease', 'diabetes', 'copd'
        ]

    class SubscriptionAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'id',
            'subscription_name',
            'online_booking_function',
            'online_payment_function',
            'vacation_function',
            'patient_manager_function',
            'clinic_number',
            'collaborator_number',
            'service_number',
            'days'
        ]

    class OptionsAdminView(ModelView):
        column_display_pk = True
        form_columns = [
            'id',
            'google_access_token',
            'google_access_expires',
            'google_refresh_token',
            'calendar_page_url',
            'calendar_availability_limit',
            'patient_booking_limit',
            'payment_online',
            'payment_offline',
            'reminder_booking_email',
            'cancel_booking_email'
        ]


    admin.add_view(ProsAdminView(Pros, db.session))
    admin.add_view(BookingsAdminView(Bookings, db.session))
    admin.add_view(ClinicsAdminView(Clinics, db.session))
    admin.add_view(ClinicServicesAdminView(ClinicServices, db.session))
    admin.add_view(ClinicInactivityAdminView(ClinicInactivity, db.session))
    admin.add_view(HubsAdminView(Hubs, db.session))
    admin.add_view(HubAvailabilitiesAdminView(HubAvailabilities, db.session))
    admin.add_view(HubServicesAdminView(HubServices, db.session))
    admin.add_view(HubInactivityAdminView(HubInactivity, db.session))
    admin.add_view(SpecializationsAdminView(Specializations, db.session))
    admin.add_view(PatientsAdminView(Patients, db.session))
    admin.add_view(ProvincesAdminView(Provinces, db.session))
    admin.add_view(PatientFormAdminView(PatientForm, db.session))
    admin.add_view(AllergiesAdminView(Allergies, db.session))
    admin.add_view(SurgeriesAdminView(Surgeries, db.session))
    admin.add_view(MedicationsAdminView(Medications, db.session))
    admin.add_view(DiseasesAdminView(Diseases, db.session))
    admin.add_view(SubscriptionAdminView(Subscriptions, db.session))
    admin.add_view(OptionsAdminView(Options, db.session))




