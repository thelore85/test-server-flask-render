from api.model import Pros, Clinics, Hubs, HubAvailabilities, HubInactivity, HubServices, ClinicServices, Patients, Bookings, db
from datetime import datetime, time, date, UTC, timedelta
import pytz

def get_current_date(clinic_id):
    clinic = Clinics.query.get(clinic_id)
    serlialized_clinic = clinic.serialize()
    time_zone = serlialized_clinic['time_zone']
    now_utc = datetime.now(UTC)
    tz = pytz.timezone(time_zone)
    now_local = now_utc.astimezone(tz)
    return (now_local)