export const initialFarmer = {
  name: "Ramesh Kumar",
  phone: "+91 98765 43210",
  village: "Rampur, Kota District, Rajasthan",
  farmerId: "RJ-KVF-2025-0891",
  bankAccount: "XXXX XXXX 4821",
  tractorNumber: "RJ-24-EG-4407",
};

export const initialProcurement = {
  slotDate: "Today",
  slotTime: "10:30 AM",
  centre: "Rampur Procurement Centre",
  lotId: "KVF102537-223",
  value: "1,25,300",
  token: "A-45",
  typeOfCrop: "Wheat",
  grossWeight: "85.34 q",
};

export const procurementSteps = [
  {
    key: "booked",
    label: "Slot booked",
    detail: "Gate entry pass generated for Token #A-45.",
  },
  {
    key: "gate",
    label: "Gate entry",
    detail: "Awaiting entry verification at Rampur Procurement Centre.",
  },
  {
    key: "weighing",
    label: "Weighing and quality check",
    detail: "Wheat lot will be weighed and graded on arrival.",
  },
  {
    key: "payment",
    label: "Payment processed",
    detail: "Payment is credited to your linked bank account.",
  },
];

export const centres = [
  "Rampur Procurement Centre",
  "Sonepat Mandi Centre",
  "Karnal Procurement Centre",
  "Ajmer Grain Market",
];

export const timeSlots = [
  "7:00 AM - 8:00 AM",
  "8:00 AM - 9:00 AM",
  "9:00 AM - 10:00 AM",
  "10:00 AM - 11:00 AM",
  "11:00 AM - 12:00 PM",
  "2:00 PM - 3:00 PM",
  "3:00 PM - 4:00 PM",
];

export const initialAlerts = [
  {
    id: 1,
    type: "info",
    title: "Gate pass ready",
    message: "Your gate entry pass for Token #A-45 is ready. Please carry a valid ID proof.",
    time: "Today, 6:02 AM",
  },
  {
    id: 2,
    type: "warning",
    title: "Slot reminder",
    message: "Your procurement slot at Rampur Procurement Centre starts in 2 hours.",
    time: "Today, 8:30 AM",
  },
  {
    id: 3,
    type: "success",
    title: "Payment credited",
    message: "₹1,08,400 was credited to your linked bank account for Lot ID KVF101982-118.",
    time: "12 Sep, 4:15 PM",
  },
];

export const faqs = [
  {
    q: "How do I book a procurement slot?",
    a: "Go to Book Slot from the sidebar, choose your nearest procurement centre, pick an available date and time, and confirm. You will receive a gate entry pass instantly.",
  },
  {
    q: "What documents should I carry to the centre?",
    a: "Carry your Aadhaar card, farmer ID, and a printed or mobile copy of your gate entry pass shown on the Dashboard.",
  },
  {
    q: "When will I receive payment after procurement?",
    a: "Payments are typically credited to your linked bank account within 3 to 5 working days after weighing and quality check are completed.",
  },
  {
    q: "Can I change my slot after booking?",
    a: "Yes, cancel the existing slot from My Procurement and book a new one from Book Slot, subject to availability.",
  },
];
