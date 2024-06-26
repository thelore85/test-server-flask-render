import os
from api.model import db, Pros, Clinics
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

    admin.add_view(ProsAdminView(Pros, db.session))    
    admin.add_view(ClinicsAdminView(Clinics, db.session))





