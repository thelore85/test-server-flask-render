import os
import smtplib
from api.model import Pros, Clinics


def send_recovery_email(user_email, token):
    print(user_email)
    user = Pros.query.filter_by(email=user_email).first()
    if not user:
        print("///////////////////NOT USER/////////////////////////////////////////")
        return False, "User email invalid"
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = user.email
    subject = 'Password Recovery'
    body = f'{front_url}/password-setting?token={token}'
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)


def send_set_password_email(user_email, token):
    print(user_email)
    user = Pros.query.filter_by(email=user_email).first()
    if not user:
        print("///////////////////NOT USER/////////////////////////////////////////")
        return False, "User email invalid"
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = user.email
    subject = 'Password Recovery'
    body = f"Congratulations {user_email}! You have been invited to work in a clinic. Please follow the link below to set your password." + f'\n\n{front_url}/password-setting?token={token}'
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)


##### Invitations from clinic to pro
        
def existing_pro_invitation_email(pro, clinic_id):
    clinic = Clinics.query.get(clinic_id)
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = pro.email
    subject = f'{clinic.name} invitation'
    body = f'Congratulations {pro.name}!\n {clinic.name} has invited you to work with them! Check out your hubs to accept the invitation.\n\n {front_url}'
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)

def non_existing_pro_invitation_email(invited_pro_email, clinic_id):
    clinic = Clinics.query.get(clinic_id)
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = invited_pro_email
    subject = f'{clinic.name} invitation'
    body = f'Congratulations!\n {clinic.name} wants you to work with them! Create an account to be invited.\n\n {front_url}/signup'
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)


##### Petitions from pro to clinic
        
def existing_owner_petition_email(owner, petitioner):
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = owner.email
    subject = f'{petitioner.name} {petitioner.lastname} collaboration petition'
    body = f'Hello {owner.name}!\n {petitioner.name} {petitioner.lastname} wants to collaborate with you. \n' + "Create a hub for them in your clinic to invite them. If you don't have a clinic, create it first\n" + f'{front_url}'
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)

def non_existing_owner_petition_email(owner_email, petitioner):
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = owner_email
    subject = f'{petitioner.name} {petitioner.lastname} collaboration petition'
    body = f'Greetings from the DocDate team!\n {petitioner.name} {petitioner.lastname} wants to collaborate with you!. \n' + "Create an account in our website, set up your clinic and invite them to join you!\n" + f'{front_url}/signup'
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)

def booking_confirmation_email(booking_data, patient_data):
    # SMTP configuration
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_username = os.getenv("EMAIL_ACCOUNT")
    smtp_password = os.getenv("EMAIL_PSW")
    # Global variables
    front_url = os.getenv("FRONT_URL")
    # email details
    from_email = 'noreply@docdate.com'
    to_email = patient_data['email']
    subject = f"Confirm your booking: {patient_data['name']}"
    body = f'Please confirm your booking clicking the button below!\n' + f"{front_url}/booking/confirmation/{booking_data['id']}"
    # message
    message = f'Subject: {subject}\n\n{body}'
    # SMTP connection and email dispatch
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)
        
def send_reminder_email(booking):
    pass