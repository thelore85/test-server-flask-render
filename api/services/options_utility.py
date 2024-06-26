from api.model import Options, Pros, db
import random

def create_unique_url(username):
    while True:
        existing_url = Options.query.filter_by(calendar_page_url=username).first()
        if not existing_url:
            return username
        username = f"{username}{random.randint(1, 1000)}"

def create_default_options(username, pro_id):
    calendar_page_url = create_unique_url(username)
    options = Options(
        calendar_page_url=calendar_page_url,
        calendar_availability_limit=60,
        patient_booking_limit=False,
        payment_online=False,
        payment_offline=False,
        reminder_booking_email=True,
        cancel_booking_email=False,
    )
    db.session.add(options)
    db.session.commit()
    pro = Pros.query.get(pro_id)
    pro.options_id = options.id
    db.session.commit()
    return options