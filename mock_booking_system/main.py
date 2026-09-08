from fastapi import FastAPI

app = FastAPI(title='KisanVanta Mock Booking System')


@app.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'mock-booking-system'}


@app.post('/bookings')
def create_booking():
    return {'status': 'mock booking received'}
