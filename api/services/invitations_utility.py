from api.model import Pros, Clinics, Hubs, HubAvailabilities, HubServices, ClinicServices, db
from flask import Blueprint, jsonify, request
from datetime import datetime, time, date, UTC

def create_hub_from_invitation(pro, clinic_id, availabilities, services, role, status):
    new_hub = Hubs(
        status = status,
        role = role,
        clinic_id = clinic_id,
        pro_id = pro.id,
        creation_date = datetime.now(UTC))
    db.session.add(new_hub)
    db.session.commit()
    final_hub_availabilities = []
    for hub_availability in availabilities:
        if 'working_day' not in hub_availability:
            return jsonify({"message": "all data are required"}), 400
        starting_hour = datetime.strptime(hub_availability['starting_hour'], '%H:%M').time()
        ending_hour = datetime.strptime(hub_availability['ending_hour'], '%H:%M').time()
        working_day = hub_availability['working_day']
        def add_availability(day):
            existing_availability = HubAvailabilities.query.filter_by(
                hub_id=new_hub.id,
                working_day=day,
                starting_hour=starting_hour,
                ending_hour=ending_hour
            ).first()
            if not existing_availability:
                new_hub_availability = HubAvailabilities(
                    working_day=day,
                    starting_hour=starting_hour,
                    ending_hour=ending_hour,
                    hub_id=new_hub.id
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
    final_hubservices = []
    for service in services:
        new_hubservice = HubServices(clinic_service_id=service.get('id'),
                                    hub_id=new_hub.id,
                                    activated = True)
        db.session.add(new_hubservice)
        db.session.commit()
        final_hubservices.append(service)
    final_hub = new_hub.serialize()
    final_hub['availabilities'] = final_hub_availabilities
    final_hub['services'] = final_hubservices
    #final_hub['availabilities'].append(final_availabilities)
    #final_hub['services'].append(final_hubservices)
    clinic = Clinics.query.get(clinic_id)
    final_clinic = clinic.serialize()
    final_clinic['hubs'] = []
    final_clinic['clinic_services'] = []
    clinic_services = ClinicServices.query.filter_by(clinic_id=clinic.id).all()
    hubs = Hubs.query.filter_by(clinic_id=clinic.id).all()
    for clinic_service in clinic_services:
        final_clinic['clinic_services'].append(clinic_service.serialize())
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
        final_clinic['hubs'].append(hub_dict)
    return {
    'final_hub': final_hub,
    'final_clinic': final_clinic
    }


