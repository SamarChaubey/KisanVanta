import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import centres, procurement, slot_requests, farmers
from services.bottleneck_monitor import run_bottleneck_monitor


@asynccontextmanager
async def lifespan(app):
    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(run_bottleneck_monitor(stop_event))
    yield
    stop_event.set()
    await monitor_task

app = FastAPI(title='KisanVanta API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(slot_requests.router, prefix='/api/slot-requests', tags=['slot requests'])
app.include_router(procurement.router, prefix='/procurement', tags=['procurement'])
app.include_router(centres.router, prefix='/centres', tags=['centres'])
app.include_router(farmers.router, prefix='/farmers', tags=['farmers'])


@app.get('/health')
def health_check():
    return {'status': 'ok'}
