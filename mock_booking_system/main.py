import os
from pathlib import Path

from fastapi import FastAPI
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import BaseModel

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME')
if not MONGODB_URI or not DB_NAME:
    raise RuntimeError('MONGODB_URI and DB_NAME must be set')

database = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)[DB_NAME]


def get_collection(name):
    return database[name]


app = FastAPI(title='KisanVanta Mock Booking System')

class BookingRequest(BaseModel):
    slotId: str
    centreId: str
    farmerId: str
    date: str
    time: str


@app.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'mock-booking-system'}


@app.get('/availability')
def get_availability(centreId: str, date: str):
    try:
        centre_id = ObjectId(centreId)
    except (InvalidId, TypeError):
        return {'centreId': centreId, 'date': date, 'slots': []}
    slots = list(get_collection('booking_slots').find({
        'centreId': centre_id,
        'date': date,
    }))
    return {
        'centreId': centreId,
        'date': date,
        'slots': [
            {
                'slotId': str(slot['_id']),
                'centreId': centreId,
                'date': slot['date'],
                'time': slot['time'],
                'capacity': slot['capacity'],
                'booked': slot['booked'],
                'status': slot['status'],
            }
            for slot in slots
        ],
    }


@app.post('/book')
def book_slot(request: BookingRequest):
    try:
        slot_id = ObjectId(request.slotId)
        centre_id = ObjectId(request.centreId)
        ObjectId(request.farmerId)
    except (InvalidId, TypeError):
        return {'status': 'rejected', 'message': 'Invalid booking identifiers'}
    result = get_collection('booking_slots').find_one_and_update(
        {
            '_id': slot_id,
            'centreId': centre_id,
            'date': request.date,
            'time': request.time,
            'status': 'available',
            '$expr': {'$lt': ['$booked', '$capacity']},
        },
        {'$inc': {'booked': 1}},
    )
    if not result:
        return {'status': 'unavailable', 'message': 'Requested slot is unavailable'}
    return {
        'status': 'confirmed',
        'slot': {
            'slotId': request.slotId,
            'centreId': request.centreId,
            'date': request.date,
            'time': request.time,
        },
    }
