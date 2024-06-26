from api.model import Pros, Clinics, Hubs, HubAvailabilities, HubInactivity, HubServices, ClinicServices, db
from datetime import datetime, time, date, UTC, timedelta
from collections import defaultdict
from api.services.date_utility import get_current_date
import pytz


def get_date_range(clinic_id):
    current_date = get_current_date(clinic_id) + timedelta(minutes=1440)
    pro = Pros.query.join(Clinics).filter_by(id=clinic_id).first()
    pro_options = pro.options
    booking_anticipation = current_date + timedelta(days=pro_options.calendar_availability_limit)
    date_list = []
    while current_date <= booking_anticipation:
        formatted_date = current_date.strftime('%Y-%m-%d')
        date_list.append({
            "date": formatted_date,
            "bookingAvailabilities": []
        })
        current_date += timedelta(days=1)
    return date_list

def get_hubs_by_clinic_service(clinic_services):
    hubs_by_clinic_service = {}
    for clinic_service in clinic_services:
        service_name = clinic_service.serialize()['serviceName']
        hubs = Hubs.query.join(HubServices).filter_by(clinic_service_id=clinic_service.id).all()
        if service_name not in hubs_by_clinic_service:
            hubs_by_clinic_service[service_name] = {}
        for hub in hubs:
            if hub.status == 'active':
                hub_service = HubServices.query.filter_by(hub_id=hub.id, clinic_service_id=clinic_service.id).first()
                if hub_service.activated == True:
                    hub_availabilities = HubAvailabilities.query.filter_by(hub_id=hub.id).all()
                    serialized_hub_availabilities = [hub_availability.serialize() for hub_availability in hub_availabilities]
                    hub_pro = hub.serialize()['pro']['name']
                    if service_name not in hubs_by_clinic_service:
                        hubs_by_clinic_service[service_name] = {}
                    if hub_pro not in hubs_by_clinic_service[service_name]:
                        hubs_by_clinic_service[service_name][hub_pro] = {}
                    hubs_by_clinic_service[service_name][hub_pro]['hubServiceId'] = hub_service.id
                    hubs_by_clinic_service[service_name][hub_pro]['availabilities'] = serialized_hub_availabilities
                    hubs_by_clinic_service[service_name][hub_pro]['id'] = hub.id
                    hubs_by_clinic_service[service_name][hub_pro]['specialization'] = clinic_service.serialize()['specialization']
    return hubs_by_clinic_service

def get_availabilities_calendar(empty_calendar, hubs_by_clinic_service):
    calendar_dict = {item["date"]: item for item in empty_calendar}
    for service_name, service_info in hubs_by_clinic_service.items():
        for pro_name, pro_info in service_info.items():
            hub_service_id = pro_info.get("hubServiceId")
            for availability in pro_info.get("availabilities", []):
                working_day = availability.get("working_day")
                for date, calendar_item in calendar_dict.items():
                    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                    if date_obj.isoweekday() == working_day:
                        calendar_item["bookingAvailabilities"].append({
                            "service": service_name,
                            "professional": pro_name,
                            "from": availability.get("starting_hour"),
                            "to": availability.get("ending_hour"),
                            "hubServiceId": hub_service_id,
                            "hubId": pro_info['id'],
                            "specialization": pro_info['specialization']
                        })
    availabilities_calendar = [{"date": date, "bookingAvailabilities": calendar_dict[date].get("bookingAvailabilities", [])}
                        for date in sorted(calendar_dict.keys())]
    return availabilities_calendar

def remove_availabilities_by_clinic_inactivity(availabilities_calendar, clinic_inactivity):
    new_calendar = []
    inactivity_start = datetime.fromisoformat(clinic_inactivity['starting_date'])
    inactivity_end = datetime.fromisoformat(clinic_inactivity['ending_date'])
    for day in availabilities_calendar:
        date = datetime.fromisoformat(day['date']).date()
        booking_availabilities = day['bookingAvailabilities']
        new_day = {'date': day['date'], 'bookingAvailabilities': []}
        for availability in booking_availabilities:
            from_time = datetime.combine(date, datetime.strptime(availability['from'], "%H:%M").time())
            to_time = datetime.combine(date, datetime.strptime(availability['to'], "%H:%M").time())
            if (from_time < inactivity_end) and (to_time > inactivity_start):
                if from_time < inactivity_start:
                    new_day['bookingAvailabilities'].append({
                        "from": availability['from'],
                        "to": inactivity_start.strftime("%H:%M"),
                        "hubServiceId": availability['hubServiceId'],
                        "professional": availability['professional'],
                        "service": availability['service'],
                        "hubId": availability['hubId'],
                        "specialization": availability['specialization']
                    })
                if to_time > inactivity_end:
                    new_day['bookingAvailabilities'].append({
                        "from": inactivity_end.strftime("%H:%M"),
                        "to": availability['to'],
                        "hubServiceId": availability['hubServiceId'],
                        "professional": availability['professional'],
                        "service": availability['service'],
                        "hubId": availability['hubId'],
                        "specialization": availability['specialization']
                    })
            else:
                new_day['bookingAvailabilities'].append(availability)
        new_calendar.append(new_day) 
    return new_calendar
        

def remove_availabilities_by_hub_inactivity(upgraded_calendar, hub_inactivity):
    new_calendar = []
    for day in upgraded_calendar:
        date = datetime.fromisoformat(day['date']).date()
        booking_availabilities = day['bookingAvailabilities']
        new_day = {'date': day['date'], 'bookingAvailabilities': []}
        for availability in booking_availabilities:
            from_time = datetime.combine(date, datetime.strptime(availability['from'], "%H:%M").time())
            to_time = datetime.combine(date, datetime.strptime(availability['to'], "%H:%M").time())
            overlaps_with_inactivity = False
            if hub_inactivity['hub_id'] == availability['hubId']:
                inactivity_start = datetime.fromisoformat(hub_inactivity['starting_date'])
                inactivity_end = datetime.fromisoformat(hub_inactivity['ending_date'])
                if (from_time < inactivity_end) and (to_time > inactivity_start):
                    overlaps_with_inactivity = True
                    if from_time < inactivity_start:
                        new_day['bookingAvailabilities'].append({
                            "from": availability['from'],
                            "hubServiceId": availability['hubServiceId'],
                            "professional": availability['professional'],
                            "service": availability['service'],
                            "to": inactivity_start.strftime("%H:%M"),
                            "hubId": availability['hubId'],
                            "specialization": availability['specialization']
                        })
                    if to_time > inactivity_end:
                        new_day['bookingAvailabilities'].append({
                            "from": inactivity_end.strftime("%H:%M"),
                            "hubServiceId": availability['hubServiceId'],
                            "professional": availability['professional'],
                            "service": availability['service'],
                            "to": availability['to'],
                            "hubId": availability['hubId'],
                            "specialization": availability['specialization']
                        })
            if not overlaps_with_inactivity:
                new_day['bookingAvailabilities'].append(availability)
        new_calendar.append(new_day)    
    return new_calendar



def remove_availabilities_by_booking(availabilities_calendar, booking):
    new_availabilities_calendar = []
    for day in availabilities_calendar:
        date = datetime.fromisoformat(day['date']).date()
        new_day = {'date': day['date'], 'bookingAvailabilities': []}
        for availability in day['bookingAvailabilities']:
            from_time = datetime.combine(date, datetime.strptime(availability['from'], "%H:%M").time())
            to_time = datetime.combine(date, datetime.strptime(availability['to'], "%H:%M").time())
            booking_start = datetime.fromisoformat(booking['date'])
            booking_duration = timedelta(minutes=booking['duration'])
            booking_end = booking_start + booking_duration
            if (from_time < booking_end) and (to_time > booking_start) and availability['hubId'] == booking['hubId']:
                if from_time < booking_start:
                    new_day['bookingAvailabilities'].append({
                        "from": from_time.time().strftime("%H:%M"),
                        "to": booking_start.time().strftime("%H:%M"),
                        "hubServiceId": availability['hubServiceId'],
                        "professional": availability['professional'],
                        "service": availability['service'],
                        "hubId": availability['hubId'],
                        "specialization": availability['specialization']
                    })
                if to_time > booking_end:
                    new_day['bookingAvailabilities'].append({
                        "from": booking_end.time().strftime("%H:%M"),
                        "to": to_time.time().strftime("%H:%M"),
                        "hubServiceId": availability['hubServiceId'],
                        "professional": availability['professional'],
                        "service": availability['service'],
                        "hubId": availability['hubId'],
                        "specialization": availability['specialization']
                    })
            else:
                new_day['bookingAvailabilities'].append(availability)
        new_availabilities_calendar.append(new_day)
    return new_availabilities_calendar

def divide_availabilities_by_service_duration(availabilities_calendar, services):
    service_duration_dict = {service['id']: service['duration'] for service in services}
    for day in availabilities_calendar:
        new_availabilities = []
        for availability in day['bookingAvailabilities']:
            service_duration = service_duration_dict.get(availability['hubServiceId'], None)
            if service_duration is None:
                continue
            from_time = datetime.strptime(availability['from'], "%H:%M")
            to_time = datetime.strptime(availability['to'], "%H:%M")
            time_slots = []
            current_time = from_time
            while current_time + timedelta(minutes=service_duration) <= to_time:
                time_slots.append(current_time.strftime("%H:%M"))
                current_time += timedelta(minutes=service_duration)
            new_availability = {
                "availabilities": time_slots,
                "hubId": availability['hubId'],
                "hubServiceId": availability['hubServiceId'],
                "professional": availability['professional'],
                "service": availability['service'],
                "specialization": availability['specialization']
            }
            new_availabilities.append(new_availability)
        day['bookingAvailabilities'] = new_availabilities
    return availabilities_calendar

def consolidate_availabilities(availabilities_calendar):
    for day in availabilities_calendar:
        consolidated_availabilities = {}
        for availability in day['bookingAvailabilities']:
            key = (availability['hubServiceId'], availability['hubId'])
            if key in consolidated_availabilities:
                consolidated_availabilities[key]['availabilities'].extend(availability['availabilities'])
            else:
                consolidated_availabilities[key] = {
                    "availabilities": availability['availabilities'],
                    "hubId": availability['hubId'],
                    "hubServiceId": availability['hubServiceId'],
                    "professional": availability['professional'],
                    "service": availability['service'],
                    "specialization": availability['specialization']
                }
        day['bookingAvailabilities'] = list(consolidated_availabilities.values())
    return availabilities_calendar



