const path = require('node:path');
const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');
const dotenv = require('dotenv');

dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

const app = express();
const port = Number(process.env.PORT || 3001);
const mongoUri = process.env.MONGODB_URI;
const databaseName = process.env.DB_NAME || 'kisanvanta';

if (!mongoUri) {
  throw new Error('MONGODB_URI is not set. Add it to the project .env file.');
}

const client = new MongoClient(mongoUri, { serverSelectionTimeoutMS: 5000 });
let database;

async function getDatabase() {
  if (!database) {
    await client.connect();
    database = client.db(databaseName);
  }

  return database;
}

function normalisePhone(phone) {
  return phone.replace(/\s+/g, '');
}

function serialiseRequest(request) {
  return {
    ...request,
    _id: request._id.toString(),
    farmerId: request.farmerId.toString(),
    centreId: request.centreId.toString(),
  };
}

app.use(cors());
app.use(express.json());

app.get('/health', async (req, res) => {
  try {
    const db = await getDatabase();
    await db.command({ ping: 1 });
    res.json({ status: 'ok', database: databaseName });
  } catch (error) {
    res.status(503).json({ status: 'error', message: 'MongoDB connection failed' });
  }
});

app.post('/api/slot-requests', async (req, res) => {
  const { farmerName, phone, centre, crop, quantity, date, time } = req.body;
  const cleanPhone = typeof phone === 'string' ? normalisePhone(phone) : '';
  const cleanName = typeof farmerName === 'string' ? farmerName.trim() : '';
  const cleanCentre = typeof centre === 'string' ? centre.trim() : '';
  const cleanCrop = typeof crop === 'string' ? crop.trim().toLowerCase() : '';
  const numericQuantity = Number(quantity);

  if (!cleanName || !/^\d{10}$/.test(cleanPhone) || !cleanCentre || !cleanCrop ||
      !/^\d{4}-\d{2}-\d{2}$/.test(date || '') || !time ||
      !Number.isInteger(numericQuantity) || numericQuantity <= 0) {
    return res.status(400).json({ message: 'Invalid slot request.' });
  }

  try {
    const db = await getDatabase();
    const users = db.collection('users');
    const centres = db.collection('procurement_centres');
    const slotRequests = db.collection('slot_requests');

    await users.updateOne(
      { phone: cleanPhone },
      {
        $set: { name: cleanName, phone: cleanPhone, role: 'farmer', updatedAt: new Date() },
        $setOnInsert: { createdAt: new Date() },
      },
      { upsert: true },
    );

    const farmer = await users.findOne({ phone: cleanPhone });
    await centres.updateOne(
      { name: cleanCentre },
      {
        $setOnInsert: {
          name: cleanCentre,
          location: {},
          crops: [cleanCrop],
          status: 'open',
          createdAt: new Date(),
        },
      },
      { upsert: true },
    );

    const procurementCentre = await centres.findOne({ name: cleanCentre });
    const now = new Date();
    const request = {
      farmerId: farmer._id,
      centreId: procurementCentre._id,
      crop: cleanCrop,
      quantity: numericQuantity,
      requestedDate: date,
      preferredTime: time,
      status: 'received',
      requestedSlot: { date, time },
      createdAt: now,
      updatedAt: now,
    };

    const result = await slotRequests.insertOne(request);
    request._id = result.insertedId;

    return res.status(201).json({ status: 'received', request: serialiseRequest(request) });
  } catch (error) {
    console.error('Unable to save slot request:', error);
    return res.status(500).json({ message: 'Unable to save slot request.' });
  }
});

app.listen(port, () => {
  console.log(`KisanVanta Node API listening on http://localhost:${port}`);
});

async function closeMongoConnection() {
  await client.close();
}

process.on('SIGINT', closeMongoConnection);
process.on('SIGTERM', closeMongoConnection);