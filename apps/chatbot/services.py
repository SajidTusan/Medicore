import re
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from apps.doctors.models import DoctorProfile
from apps.appointments.services import get_available_slots


SPECIALTIES = {
    "cardiology": ["cardiology", "cardiologist", "heart", "হার্ট", "হৃদরোগ"],
    "dermatology": ["dermatology", "dermatologist", "skin", "ত্বক"],
    "neurology": ["neurology", "neurologist", "brain", "মস্তিষ্ক"],
    "orthopedics": ["orthopedic", "orthopedics", "bone", "হাড়"],
    "gynecology": ["gynecology", "gynecologist", "গাইনি"],
    "pediatrics": ["pediatrics", "pediatrician", "child doctor", "শিশু"],
    "medicine": ["medicine specialist", "general physician", "মেডিসিন"],
}


def detect_date(message):
    today = timezone.localdate()
    text = message.lower()

    if "day after tomorrow" in text or "পরশু" in text:
        return today + timedelta(days=2)

    if "tomorrow" in text or "আগামীকাল" in text or "কাল" in text:
        return today + timedelta(days=1)

    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if match:
        from datetime import date

        try:
            return date.fromisoformat(match.group(1))
        except ValueError:
            return None

    return None


def detect_specialty(message):
    text = message.lower()

    for specialty, keywords in SPECIALTIES.items():
        if any(keyword in text for keyword in keywords):
            return specialty

    return None


def handle_message(message):
    text = message.strip()

    if not text:
        return {
            "reply": "Please type a message. আপনার কী সাহায্য দরকার?",
            "doctors": [],
        }

    lowered = text.lower()

    if any(word in lowered for word in [
        "hello", "hi", "হ্যালো", "সালাম", "assalamu"
    ]):
        return {
            "reply": (
                "Welcome to MediCore! I can help you find doctors "
                "and check appointment availability. "
                "আপনি কোন ধরনের ডাক্তার খুঁজছেন?"
            ),
            "doctors": [],
        }

    specialty = detect_specialty(text)
    appointment_intent = any(word in lowered for word in [
        "appointment", "available", "slot", "book",
        "schedule", "সময়", "অ্যাপয়েন্টমেন্ট", "বুকিং",
    ])

    if specialty:
        keywords = SPECIALTIES[specialty]

        specialty_query = Q()
        for keyword in keywords:
            specialty_query |= (
                Q(specialization__icontains=keyword)
                | Q(department__name__icontains=keyword)
            )

        doctors = list(
            DoctorProfile.objects.filter(
                specialty_query,
                user__is_active=True,
            ).select_related(
                "user", "hospital", "department"
            )[:10]
        )

        requested_date = detect_date(text)
        doctor_results = []

        for doctor in doctors:
            slots = []
            if requested_date and requested_date >= timezone.localdate():
                slots = get_available_slots(doctor, requested_date)

            doctor_results.append({
                "id": doctor.id,
                "name": doctor.user.get_full_name() or doctor.user.username,
                "specialization": doctor.specialization,
                "hospital": doctor.hospital.name if doctor.hospital else "",
                "department": doctor.department.name if doctor.department else "",
                "fee": str(doctor.consultation_fee),
                "date": requested_date.isoformat() if requested_date else "",
                "slots": [
                    {
                        "start": slot["start_time"].strftime("%H:%M"),
                        "end": slot["end_time"].strftime("%H:%M"),
                        "booking_url": (
                            f"/appointments/book/{doctor.id}/"
                            f"?date={requested_date.isoformat()}"
                            f"&start_time={slot['start_time'].strftime('%H:%M')}"
                            f"&end_time={slot['end_time'].strftime('%H:%M')}"
                        ),
                    }
                    for slot in slots[:8]
                ],
            })

        if not doctors:
            return {
                "reply": (
                    f"I couldn't find a doctor matching {specialty}. "
                    "Try another specialty or search from the Doctors page."
                ),
                "doctors": [],
            }

        if requested_date and requested_date < timezone.localdate():
            return {
                "reply": "That date is in the past. Please provide a future date.",
                "doctors": [],
            }

        if requested_date:
            for item in doctor_results:
                if not item["slots"]:
                    item["availability_message"] = (
                        "No available slots found for this date."
                    )

            reply = (
                f"Here are matching {specialty} doctors for "
                f"{requested_date.isoformat()}. Choose an available slot to continue."
            )
        else:
            reply = (
                f"I found {len(doctor_results)} matching {specialty} doctor(s). "
                "Tell me a date, such as tomorrow or 2026-10-15, "
                "to check available slots."
            )

        return {"reply": reply, "doctors": doctor_results}

    if appointment_intent:
        return {
            "reply": (
                "To check appointments, tell me the doctor specialty and date. "
                "Example: cardiologist tomorrow. "
                "ডাক্তারের ধরন ও তারিখ লিখুন।"
            ),
            "doctors": [],
        }

    return {
        "reply": (
            "I can help search doctors and check available appointment slots. "
            "Try: 'cardiologist tomorrow' or 'চর্মরোগ বিশেষজ্ঞ 2026-10-15'."
        ),
        "doctors": [],
    }