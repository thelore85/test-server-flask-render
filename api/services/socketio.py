# from app import socketio
from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_clinic')
def handle_join_clinic(data):
    clinic_id = data['clinic_id']
    join_room(clinic_id)
    print(f'Client joined clinic room {clinic_id}')

@socketio.on('leave_clinic')
def handle_leave_clinic(data):
    clinic_id = data['clinic_id']
    leave_room(clinic_id)
    print(f'Client left clinic room {clinic_id}')



