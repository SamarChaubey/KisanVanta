from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from typing import Literal

from database import get_collection
from services.bottleneck_monitor import risk_assessment

router = APIRouter()


class CropPriceUpdate(BaseModel):
    crop: str
    pricePerBag: float = Field(gt=0)


class Crop(BaseModel):
    name: str = Field(min_length=1)
    pricePerBag: float = Field(gt=0)


class CentreCreate(BaseModel):
    name: str = Field(min_length=1)
    location: dict[str, str] = {}
    crops: list[Crop] = []
    dailyCapacity: int = Field(default=0, ge=0)
    processingRate: int = Field(default=0, ge=0)
    storageCapacity: int = Field(default=0, ge=0)
    currentStorage: int = Field(default=0, ge=0)
    liftingCapacity: int = Field(default=0, ge=0)
    status: Literal['open', 'closed'] = 'open'


class CentreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    location: dict[str, str] | None = None
    crops: list[Crop] | None = None
    dailyCapacity: int | None = Field(default=None, ge=0)
    processingRate: int | None = Field(default=None, ge=0)
    storageCapacity: int | None = Field(default=None, ge=0)
    currentStorage: int | None = Field(default=None, ge=0)
    liftingCapacity: int | None = Field(default=None, ge=0)
    status: Literal['open', 'closed'] | None = None


class CropCreate(BaseModel):
    name: str = Field(min_length=1)
    pricePerBag: float = Field(gt=0)


def _object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail='Invalid centreId') from None


def _crop_name(crop):
    return crop if isinstance(crop, str) else crop.get('name')


@router.get('/')
def list_centres():
    centres = list(get_collection('procurement_centres').find())
    for c in centres:
        c['_id'] = str(c['_id'])
    return centres


def _risk_snapshot(snapshot):
    snapshot = dict(snapshot)
    for key in ('_id', 'centreId'):
        if key in snapshot:
            snapshot[key] = str(snapshot[key])
    if 'createdAt' in snapshot:
        snapshot['createdAt'] = snapshot['createdAt'].isoformat()
    return snapshot


def _latest_risk(centre):
    status = get_collection('centre_status').find_one({'centreId': centre['_id']}) or {}
    snapshot = get_collection('risk_snapshots').find_one(
        {'centreId': centre['_id']},
        sort=[('createdAt', -1)],
    )
    if snapshot:
        return {
            key: value for key, value in _risk_snapshot(snapshot).items()
            if key != '_id'
        }
    return risk_assessment(centre, status)


@router.get('/risk')
def list_centre_risks():
    centres = list(get_collection('procurement_centres').find({'status': 'open'}))
    result = []
    for centre in centres:
        result.append({
            'centreId': str(centre['_id']),
            'centreName': centre['name'],
            **_latest_risk(centre),
        })
    return result


@router.get('/risk/history')
def list_risk_history(centreId: str | None = None, limit: int = 100):
    query = {}
    if centreId:
        query['centreId'] = _object_id(centreId)
    snapshots = get_collection('risk_snapshots').find(query).sort('createdAt', -1).limit(
        min(max(limit, 1), 500),
    )
    return [_risk_snapshot(snapshot) for snapshot in snapshots]


@router.get('/{centre_id}/risk')
def get_centre_risk(centre_id: str):
    oid = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one({'_id': oid, 'status': 'open'})
    if not centre:
        raise HTTPException(status_code=404, detail='Centre not found')
    return {
        'centreId': centre_id,
        'centreName': centre['name'],
        **_latest_risk(centre),
    }


@router.get('/notifications')
def list_notifications(active_only: bool = True):
    query = {'recipientRole': 'procurement_officer'}
    if active_only:
        query['active'] = True
    notifications = list(
        get_collection('notifications').find(query).sort('createdAt', -1),
    )
    for notification in notifications:
        notification['_id'] = str(notification['_id'])
        notification['centreId'] = str(notification['centreId'])
    return notifications


@router.get('/{centre_id}/notifications')
def list_centre_notifications(centre_id: str, active_only: bool = True):
    oid = _object_id(centre_id)
    query = {
        'centreId': oid,
        'recipientRole': 'procurement_officer',
    }
    if active_only:
        query['active'] = True
    notifications = list(
        get_collection('notifications').find(query).sort('createdAt', -1),
    )
    for notification in notifications:
        notification['_id'] = str(notification['_id'])
        notification['centreId'] = str(notification['centreId'])
    return notifications


@router.post('/')
def create_centre(centre: CentreCreate):
    data = centre.model_dump()
    existing = get_collection('procurement_centres').find_one({'name': data['name']})
    if existing:
        raise HTTPException(status_code=409, detail='Centre already exists')

    data['_id'] = ObjectId()
    result = get_collection('procurement_centres').insert_one(data)
    data['_id'] = str(result.inserted_id)
    return data


@router.patch('/{centre_id}')
def update_centre(centre_id: str, update: CentreUpdate):
    oid = _object_id(centre_id)
    changes = update.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail='No centre fields to update')

    if 'name' in changes:
        duplicate = get_collection('procurement_centres').find_one(
            {'name': changes['name'], '_id': {'$ne': oid}},
        )
        if duplicate:
            raise HTTPException(status_code=409, detail='Centre already exists')

    result = get_collection('procurement_centres').find_one_and_update(
        {'_id': oid},
        {'$set': changes},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail='Centre not found')
    result['_id'] = str(result['_id'])
    return result


@router.post('/{centre_id}/crops')
def add_crop(centre_id: str, crop: CropCreate):
    oid = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one({'_id': oid})
    if not centre:
        raise HTTPException(status_code=404, detail='Centre not found')
    if any(_crop_name(existing) == crop.name for existing in centre.get('crops', [])):
        raise HTTPException(status_code=409, detail='Crop already exists at this centre')

    get_collection('procurement_centres').update_one(
        {'_id': oid},
        {'$push': {'crops': crop.model_dump()}},
    )
    return {'status': 'added', 'crop': crop.model_dump()}


@router.patch('/{centre_id}/crops/{crop_name}')
def update_crop(centre_id: str, crop_name: str, update: CropCreate):
    oid = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one({'_id': oid})
    if not centre:
        raise HTTPException(status_code=404, detail='Centre not found')

    crops = centre.get('crops', [])
    if not any(_crop_name(crop) == crop_name for crop in crops):
        raise HTTPException(status_code=404, detail='Crop not found')
    if update.name != crop_name and any(_crop_name(crop) == update.name for crop in crops):
        raise HTTPException(status_code=409, detail='Crop already exists at this centre')

    updated_crops = [
        update.model_dump() if _crop_name(crop) == crop_name else crop
        for crop in crops
    ]
    get_collection('procurement_centres').update_one(
        {'_id': oid},
        {'$set': {'crops': updated_crops}},
    )
    return {'status': 'updated', 'crop': update.model_dump()}


@router.delete('/{centre_id}/crops/{crop_name}')
def remove_crop(centre_id: str, crop_name: str):
    oid = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one({'_id': oid})
    if not centre:
        raise HTTPException(status_code=404, detail='Centre not found')

    updated_crops = [
        crop for crop in centre.get('crops', [])
        if _crop_name(crop) != crop_name
    ]
    if len(updated_crops) == len(centre.get('crops', [])):
        raise HTTPException(status_code=404, detail='Crop not found')

    get_collection('procurement_centres').update_one(
        {'_id': oid},
        {'$set': {'crops': updated_crops}},
    )
    return {'status': 'removed', 'crop': crop_name}


@router.get('/{centre_id}/crop-price')
def get_crop_price(centre_id: str, crop: str):
    oid = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one(
        {'_id': oid},
        {'crops': 1, 'name': 1},
    )
    if not centre:
        raise HTTPException(status_code=404, detail='Centre or crop not found')
    selected_crop = next(
        (item for item in centre.get('crops', []) if _crop_name(item) == crop),
        None,
    )
    if selected_crop is None:
        raise HTTPException(status_code=404, detail='Centre or crop not found')
    if isinstance(selected_crop, str):
        selected_crop = {'name': selected_crop, 'pricePerBag': 0}
    return {
        'centreId': centre_id,
        'centreName': centre['name'],
        'crop': selected_crop['name'],
        'pricePerBag': selected_crop.get('pricePerBag', 0),
    }


@router.patch('/{centre_id}/crop-price')
def update_crop_price(centre_id: str, update: CropPriceUpdate):
    oid = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one({'_id': oid})
    if not centre:
        raise HTTPException(status_code=404, detail='Centre not found')

    crops = centre.get('crops', [])
    if not any(_crop_name(crop) == update.crop for crop in crops):
        raise HTTPException(status_code=404, detail='Centre or crop not found')
    updated_crops = [
        {'name': crop, 'pricePerBag': update.pricePerBag}
        if isinstance(crop, str) and crop == update.crop
        else {**crop, 'pricePerBag': update.pricePerBag}
        if _crop_name(crop) == update.crop
        else crop
        for crop in crops
    ]
    get_collection('procurement_centres').update_one(
        {'_id': oid},
        {'$set': {'crops': updated_crops}},
    )
    return {'status': 'updated', 'crop': update.crop, 'pricePerBag': update.pricePerBag}