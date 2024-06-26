
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

    

        


   
        




