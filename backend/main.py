from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import centres, procurement, slot_requests

app = FastAPI(title='KisanVanta API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(slot_requests.router, prefix='/slot-requests', tags=['slot requests'])
app.include_router(procurement.router, prefix='/procurement', tags=['procurement'])
app.include_router(centres.router, prefix='/centres', tags=['centres'])


@app.get('/health')
def health_check():
    return {'status': 'ok'}
