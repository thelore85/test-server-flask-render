from api.model import db, PatientForm, Surgeries, Allergies, Medications, Diseases
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

def create_new_allergies(allergies):
    new_allergies = Allergies(
        no_allergies = allergies['allergyNothingToDeclare'],
        other = allergies['allergyOther'],
        aspirin = allergies['allergyAspirin'],
        penicillin = allergies['allergyPenicillin'],
        sulfa_drugs = allergies['allergySulfaDrugs'],
        nsaids = allergies['allergyNSAIDs'],
        chemotherapy = allergies['allergyChemotherapyDrugs']
    )
    db.session.add(new_allergies)
    return new_allergies

def create_new_surgeries(surgeries):
    new_surgeries = Surgeries(
        no_surgeries = surgeries['surgeryNothingToDeclare'],
        other = surgeries['surgeryOther'],
        appendectomy = surgeries['surgeryAppendectomy'],
        cholecystectomy = surgeries['surgeryCholecystectomy'],
        csection = surgeries['surgeryCsection'],
        mastectomy = surgeries['surgeryMastectomy']
    )
    db.session.add(new_surgeries)
    return new_surgeries

def create_new_medications(medications):
    new_medications = Medications(
        no_medications = medications['medicationNothingToDeclare'],
        other = medications['medicationOther'],
        antihypertensives = medications['medicationAntihypertensives'],
        statins = medications['medicationStatins'],
        diabetes = medications['medicationDiabetesMedications'],
        thyroid = medications['medicationThyroidMedications'],
        anticoagulants = medications['medicationAnticoagulants']
    )
    db.session.add(new_medications)
    return new_medications

def create_new_diseases(diseases):
    new_diseases = Diseases(
        no_diseases = diseases['diseaseNothingToDeclare'],
        other = diseases['diseaseOther'],
        hypertension = diseases['diseaseHypertension'],
        diabetes = diseases['diseaseDiabetes'],
        heart_disease = diseases['diseaseHeartDisease'],
        copd = diseases['diseaseCOPD']
    )
    db.session.add(new_diseases)
    return new_diseases

def update_patient_form(form):
    try:
        allergies = form['allergies']
        former_allergies = Allergies.query.get(allergies['id'])
        former_allergies.no_allergies = allergies['nothingToDeclare']
        former_allergies.other = allergies['other']
        former_allergies.aspirin = allergies['aspirin']
        former_allergies.penicillin = allergies['penicillin']
        former_allergies.sulfa_drugs = allergies['sulfaDrugs']
        former_allergies.nsaids = allergies['NSAIDs']
        former_allergies.chemotherapy = allergies['chemotherapyDrugs']
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"SQLAlchemy Error while updating allergies: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error while updating allergies: {str(e)}"}, 500

    try:    
        medications = form['medications']
        former_medications = Medications.query.get(medications['id'])
        former_medications.no_medications = medications['nothingToDeclare']
        former_medications.other = medications['other']
        former_medications.antihypertensives = medications['antihypertensives']
        former_medications.statins = medications['statins']
        former_medications.diabetes = medications['diabetesMedications']
        former_medications.thyroid = medications['thyroidMedications']
        former_medications.anticoagulants = medications['anticoagulants']
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"SQLAlchemy Error while updating medications: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error while updating medications: {str(e)}"}, 500
    
    try:
        surgeries = form['surgeries']
        former_surgeries = Surgeries.query.get(surgeries['id'])
        former_surgeries.no_surgeries = surgeries['nothingToDeclare']
        former_surgeries.other = surgeries['other']
        former_surgeries.appendectomy = surgeries['appendectomy']
        former_surgeries.cholecystectomy = surgeries['cholecystectomy']
        former_surgeries.csection = surgeries['csection']
        former_surgeries.mastectomy = surgeries['mastectomy']
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"SQLAlchemy Error while updating surgeries: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error while updating surgeries: {str(e)}"}, 500 

    try:   
        diseases = form['diseases']
        former_diseases = Diseases.query.get(diseases['id'])
        former_diseases.no_diseases = diseases['nothingToDeclare']
        former_diseases.other = diseases['other']
        former_diseases.hypertension = diseases['hypertension']
        former_diseases.diabetes = diseases['diabetes']
        former_diseases.heart_disease = diseases['heartDisease']
        former_diseases.copd = diseases['copd']
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"SQLAlchemy Error while updating diseases: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error while updating diseases: {str(e)}"}, 500
    
    try:
        former_form = PatientForm.query.get(form['id'])
        former_form.birth_date = datetime.strptime(form['birthDate'], '%Y-%m-%d')
        former_form.sex = form['sex']
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"SQLAlchemy Error while updating main form: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error while updating main form: {str(e)}"}, 500
    
    db.session.commit()
    return {"message": "Patient form updated succesfully!", "data": former_form.serialize()}
    
    


