from datetime import datetime, timezone
from bson import ObjectId
from database import get_collection

now = datetime.now(timezone.utc)

user_id = ObjectId()
centre_id = ObjectId()
slot_request_id = ObjectId()
procurement_id = ObjectId()

def seed():
    get_collection("users").insert_one({
        "_id": user_id,
        "name": "Ramesh Kumar",
        "phone": "9876543210",
        "role": "farmer",
        "village": "Village A",
        "fpoId": None,
        "centreId": centre_id,
        "createdAt": now
    })

    get_collection("procurement_centres").insert_one({
        "_id": centre_id,
        "name": "Jaipur Wheat Procurement Centre",
        "location": {"district": "Jaipur", "state": "Rajasthan"},
        "crops": [
            {"name": "wheat", "pricePerBag": 2500},
            {"name": "mustard", "pricePerBag": 3000}
        ],
        "dailyCapacity": 5000,
        "processingRate": 80,
        "storageCapacity": 20000,
        "currentStorage": 12000,
        "liftingCapacity": 3000,
        "status": "open"
    })

    get_collection("booking_slots").insert_one({
        "centreId": centre_id,
        "date": "2026-09-10",
        "time": "11:00",
        "capacity": 20,
        "booked": 12,
        "status": "available"
    })

    get_collection("slot_requests").insert_one({
        "_id": slot_request_id,
        "farmerId": user_id,
        "centreId": centre_id,
        "crop": "wheat",
        "quantity": 50,
        "requestedDate": "2026-09-10",
        "preferredTime": "11:00",
        "status": "confirmed",
        "requestedSlot": {"date": "2026-09-10", "time": "11:00"},
        "suggestedSlot": {"date": "2026-09-10", "time": "11:30"},
        "finalSlot": {"date": "2026-09-10", "time": "11:30"},
        "createdAt": now,
        "updatedAt": now
    })

    get_collection("procurement_records").insert_one({
        "_id": procurement_id,
        "farmerId": user_id,
        "slotRequestId": slot_request_id,
        "centreId": centre_id,
        "crop": "wheat",
        "quantity": 50,
        "queueNumber": 27,
        "status": "assaying",
        "quality": {"status": "accepted", "grade": "A"},
        "expectedValue": 125000,
        "actualValue": None,
        "createdAt": now,
        "updatedAt": now
    })

    get_collection("centre_status").insert_one({
        "centreId": centre_id,
        "farmersWaiting": 150,
        "processingRate": 80,
        "storageUsed": 12000,
        "storageCapacity": 20000,
        "liftingRate": 3000,
        "updatedAt": now
    })

    get_collection("simulations").insert_one({
        "centreId": centre_id,
        "scenarioName": "30% increase in arrivals",
        "inputs": {"arrivalIncrease": 30, "processingChange": 0, "liftingChange": 0},
        "result": {
            "expectedQueue": 195,
            "expectedDelayHours": 2.5,
            "storagePressure": "medium",
            "overallRisk": "high"
        },
        "createdAt": now
    })

    get_collection("financial_exposure").insert_one({
        "farmerId": user_id,
        "procurementId": procurement_id,
        "quantity": 50,
        "expectedPricePerBag": 2500,
        "expectedValue": 125000,
        "delayDays": 2,
        "scenarios": {
            "acceptedValue": 125000,
            "downgradedValue": 115000,
            "rejectedValue": 0
        },
        "estimatedExposure": 10000,
        "createdAt": now
    })

    print("Seed done.")


if __name__ == "__main__":
    seed()