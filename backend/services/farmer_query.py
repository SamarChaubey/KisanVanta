from bson import ObjectId
from bson.errors import InvalidId

from database import get_collection
from services.operational_context import gather_farmer_operational_context
from services.ollama_client import generate_answer


def _object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise ValueError('Invalid farmerId')


def _gather_context(farmer_id_str):
    oid = _object_id(farmer_id_str)

    farmer = get_collection('users').find_one({'_id': oid})
    if not farmer:
        raise ValueError('Farmer not found')

    slot_requests = list(get_collection('slot_requests').find({'farmerId': oid}))
    procurement_records = list(get_collection('procurement_records').find({'farmerId': oid}))
    financial_exposure = list(get_collection('financial_exposure').find({'farmerId': oid}))

    centre_ids = {sr['centreId'] for sr in slot_requests} | {pr['centreId'] for pr in procurement_records}
    if farmer.get('centreId'):
        centre_ids.add(farmer['centreId'])
    centres = {c['_id']: c for c in get_collection('procurement_centres').find({'_id': {'$in': list(centre_ids)}})}

    lines = [f"Farmer: {farmer['name']}, phone {farmer['phone']}"]

    for sr in slot_requests:
        centre = centres.get(sr['centreId'])
        centre_name = centre['name'] if centre else 'unknown centre'
        lines.append(
            f"Slot request: crop {sr['crop']}, quantity {sr['quantity']} bags, "
            f"centre {centre_name}, status {sr['status']}, "
            f"requested slot {sr.get('requestedSlot')}, final slot {sr.get('finalSlot')}"
        )

    for pr in procurement_records:
        centre = centres.get(pr['centreId'])
        centre_name = centre['name'] if centre else 'unknown centre'
        lines.append(
            f"Procurement record: crop {pr['crop']}, quantity {pr['quantity']} bags, "
            f"centre {centre_name}, status {pr['status']}, queue number {pr['queueNumber']}, "
            f"quality {pr['quality']}, expected value {pr['expectedValue']}"
        )

    for fe in financial_exposure:
        lines.append(
            f"Financial exposure: expected value {fe['expectedValue']}, "
            f"delay days {fe['delayDays']}, estimated exposure {fe['estimatedExposure']}, "
            f"scenarios {fe['scenarios']}"
        )

    if len(lines) == 1:
        lines.append("No slot requests or procurement records found for this farmer yet.")

    lines.append(
        'Live centre operations, available slots, active bottlenecks, and alerts:\n'
        f'{gather_farmer_operational_context(centre_ids)}'
    )
    return "\n".join(lines)


def answer_farmer_query(farmer_id_str, question, language='en'):
    context = _gather_context(farmer_id_str)
    language_instruction = (
        'Respond entirely in Hindi using Devanagari script.'
        if language == 'hi'
        else 'Respond entirely in clear, simple English.'
    )
    prompt = (
        "You are an assistant helping an Indian farmer understand their crop procurement status. "
        "Answer clearly and simply using only the facts given below. "
        "Do not invent numbers or slots not present in the data. "
        "When asked for the best slot, recommend only an available slot from the live data, "
        "mention active bottlenecks, and explain uncertainty instead of promising an outcome. "
        f"{language_instruction}\n\n"
        f"Farmer data:\n{context}\n\n"
        f"Farmer's question: {question}\n\n"
        "Answer:"
    )
    return generate_answer(prompt)