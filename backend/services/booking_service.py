import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode


BOOKING_SYSTEM_URL = os.getenv(
    'MOCK_BOOKING_SYSTEM_URL',
    'http://localhost:8001',
).rstrip('/')


class BookingSystemError(Exception):
    """Raised when the separate booking system cannot fulfil a request."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def _request(method, path, payload=None):
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    request = Request(
        f'{BOOKING_SYSTEM_URL}{path}',
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        message = 'Booking system rejected the booking request'
        try:
            body = json.loads(error.read().decode('utf-8'))
            message = body.get('detail', message)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        raise BookingSystemError(message, error.code) from error
    except (URLError, TimeoutError) as error:
        raise BookingSystemError('Booking system is unavailable') from error


def get_availability(centre_id, date):
    query = urlencode({'centreId': centre_id, 'date': date})
    return _request('GET', f'/availability?{query}')


def book_slot(slot, farmer_id):
    return _request(
        'POST',
        '/book',
        {
            'slotId': str(slot['_id']),
            'centreId': str(slot['centreId']),
            'farmerId': farmer_id,
            'date': slot['date'],
            'time': slot['time'],
        },
    )
