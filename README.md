````markdown
# KisanVanta

KisanVanta is a farmer-focused procurement platform that reduces uncertainty around procurement slots, queues, procurement status, and financial impact.

## What KisanVanta Does

1. Farmer requests a procurement slot.
2. KisanVanta's scheduling layer checks the booking system.
3. If the requested slot is available, it is booked.
4. If unavailable, KisanVanta suggests the closest available slot.
5. The confirmed slot is shown to the farmer.
6. The farmer can track procurement status and queue position.
7. KisanVanta identifies procurement bottlenecks.
8. What-if simulation shows how changes in arrivals, processing, storage, or lifting affect delays.
9. The system estimates potential financial exposure.

## Main Flow

Farmer → Slot Request → Scheduling Layer → Booking System → Confirmed Slot / Closest Available Slot → Procurement Tracking → Queue & Bottleneck Monitoring → What-If Simulation → Financial Exposure

## Key Innovation

KisanVanta does not replace the existing booking system.

It introduces an intermediary scheduling layer that:

- Receives farmer requests
- Applies KisanVanta's scheduling rules
- Checks slot availability
- Books an available slot
- Suggests the closest available slot when the requested slot is unavailable
- Shows confirmation only after the booking system confirms it

## Current MVP

- Farmer dashboard
- Procurement slot request
- Slot scheduling
- Closest available slot suggestion
- Booking confirmation
- Procurement status
- Queue monitoring
- Bottleneck identification
- What-if simulation
- Financial exposure estimation

AI/ML is not required for the current MVP. The prototype uses rules, calculations, and simulation.

## Tech Stack

- React + Vite
- FastAPI
- Python
- MongoDB Atlas
- PyMongo
- REST API

## Project Structure

```text
kisanvanta/
├── frontend/
│   └── React + Vite application
├── backend/
│   ├── FastAPI application
│   ├── scheduling logic
│   ├── procurement logic
│   └── MongoDB connection
├── mock_booking_system/
│   └── Separate FastAPI booking service
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
````

## MongoDB

One MongoDB Atlas cluster is used.

Database:

```text
kisanvanta
```

Collections:

```text
users
procurement_centres
booking_slots
slot_requests
procurement_records
centre_status
simulations
financial_exposure
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd kisanvanta
```

### 2. Configure MongoDB

Copy `.env.example` to `.env` and add your MongoDB Atlas connection string:

```env
MONGODB_URI=your_mongodb_connection_string
```

Do not upload `.env` to GitHub.

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start the Node API

The standalone slot request page sends requests to the Node API. The Node API
uses the same root `.env`, MongoDB database, and collections as the Python
backend and `seed_data.py`.

```bash
cd node-backend
npm install
npm start
```

The API listens on `http://localhost:3001`. Check the MongoDB connection at
`http://localhost:3001/health`.

### 5. Seed MongoDB

From the repository root, after configuring `.env`:

```bash
cd backend
python seed_data.py
```

### 6. Start the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 7. Start the mock booking system

Open another terminal:

```bash
cd mock_booking_system
uvicorn main:app --reload --port 8001
```

### 8. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Booking Logic

```text
Slot Request
     ↓
Check Requested Slot
     ↓
Available?
  /       \
Yes       No
 |         |
Book      Find closest
 |         |
Confirm   Suggest
           |
       User accepts
           |
         Book
           |
        Confirm
```

A slot is marked as `CONFIRMED` only after the booking system returns a successful confirmation.

## Future Scope

* Integration with real procurement and booking systems
* Real-time centre data
* More advanced scheduling
* API-based AI/ML forecasting after sufficient real-world data is available

```
```
## Setup

1. Copy `.env.example` to `.env` and set `MONGODB_URI` to your MongoDB Atlas connection string.
2. Install backend dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend from `backend/`:

   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. Start the mock booking system from `mock_booking_system/`:

   ```bash
   uvicorn main:app --reload --port 8001
   ```

5. Install and start the frontend from `frontend/`:

   ```bash
   npm install
   npm run dev
   ```
