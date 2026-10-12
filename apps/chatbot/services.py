import re
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.appointments.models import Appointment
from apps.appointments.services import get_available_slots
from apps.doctors.models import DoctorProfile
from apps.schedule_manager.models import Schedule
from .guided import handle_guided_message


SPECIALTIES = {
    "cardiology": ["cardiology", "cardiologist", "heart", "হার্ট", "হৃদরোগ", "হৃদরোগ বিশেষজ্ঞ"],
    "dermatology": ["dermatology", "dermatologist", "skin", "ত্বক", "চর্মরোগ", "চর্মরোগ বিশেষজ্ঞ"],
    "neurology": ["neurology", "neurologist", "brain", "মস্তিষ্ক", "স্নায়ু", "নিউরোলজি"],
    "orthopedics": ["orthopedic", "orthopedics", "bone", "হাড়", "অর্থোপেডিক"],
    "gynecology": ["gynecology", "gynecologist", "গাইনি", "স্ত্রীরোগ"],
    "pediatrics": ["pediatrics", "pediatrician", "child doctor", "শিশু", "শিশু বিশেষজ্ঞ"],
    "medicine": ["medicine specialist", "general physician", "internal medicine", "মেডিসিন", "মেডিসিন বিশেষজ্ঞ"],
    "ent": ["ent", "ear nose throat", "otolaryngology", "কান নাক গলা", "ইএনটি"],
    "gastroenterology": ["gastroenterology", "gastroenterologist", "digestive", "পাকস্থলী", "গ্যাস্ট্রো"],
    "ophthalmology": ["ophthalmology", "ophthalmologist", "eye doctor", "চোখ", "চক্ষু"],
    "endocrinology": ["endocrinology", "endocrinologist", "diabetes specialist", "ডায়াবেটিস", "এন্ডোক্রাইন"],
}

EMERGENCY_KEYWORDS = (
    "chest pain", "difficulty breathing", "can't breathe", "cannot breathe",
    "unconscious", "severe bleeding", "stroke", "heart attack", "suicidal",
    "বুকে ব্যথা", "শ্বাস নিতে পারছি না", "শ্বাসকষ্ট", "অজ্ঞান", "অতিরিক্ত রক্তপাত",
)

AVAILABILITY_KEYWORDS = (
    "available", "availability", "free doctor", "free slot", "open slot", "slots",
    "who is on duty", "on duty", "doctor today", "doctors today", "doctor tomorrow",
    "appointment", "schedule", "booking", "slot", "ডাক্তার আছে", "ডাক্তার দেখাও",
    "ডাক্তার দেখাতে", "ডাক্তার পাব", "ডাক্তার পাওয়া", "ডাক্তার পাওয়া", "চেম্বার",
    "আজকের ডাক্তার", "আজকে ডাক্তার", "আগামীকালের ডাক্তার", "ফাঁকা সময়", "খালি সময়",
    "অ্যাপয়েন্টমেন্ট", "অ্যাপয়েন্টমেন্ট", "সময়", "সময়", "স্লট", "বুকিং",
)

DOCTOR_KEYWORDS = (
    "doctor", "doctors", "ডাক্তার", "ডাক্তার", "daktar", "doctor list", "physician",
)

APPOINTMENT_KEYWORDS = (
    "my appointment", "my appointments", "my booking", "আমার অ্যাপয়েন্টমেন্ট",
    "আমার অ্যাপয়েন্টমেন্ট", "আমার appointment", "আমার বুকিং", "আমার booking",
)

ASSISTANT_INSTRUCTIONS = """You are MediCore's care navigation assistant. Be warm, brief, and clear. You may explain general health concepts and help people navigate MediCore, but you are not a clinician. Never diagnose, prescribe, recommend changing medication, or claim certainty about an individual's condition. Encourage a qualified healthcare professional for personal medical concerns. For emergency symptoms, tell the person to contact local emergency services or go to the nearest emergency department now. Do not ask for names, account details, or other identifying information. Do not claim to book appointments; the site must be used to complete a booking. Respond in the language the user used (Bangla or English). Use the MediCore database for doctors, schedules, appointment slots, and the signed-in patient's own appointment information; never invent those facts."""


def ai_reply(message):
    """Use OpenAI only for general care information, never as the source of app data."""
    if not getattr(settings, "OPENAI_API_KEY", ""):
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=20.0, max_retries=1)
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=ASSISTANT_INSTRUCTIONS,
            input=message,
            max_output_tokens=350,
        )
        return response.output_text.strip() or None
    except Exception:
        return None


def normalize_digits(text):
    bangla = "০১২৩৪৫৬৭৮৯"
    ascii_digits = "0123456789"
    return text.translate(str.maketrans(bangla, ascii_digits))


def detect_date(message):
    """Parse common English/Bangla relative dates and explicit calendar dates."""
    today = timezone.localdate()
    text = normalize_digits(message.lower())

    if any(word in text for word in ("day after tomorrow", "পরশু")):
        return today + timedelta(days=2)
    if any(word in text for word in ("tomorrow", "আগামীকাল", "আগামী কাল", "কালকে", "কাল")):
        return today + timedelta(days=1)
    if any(word in text for word in ("today", "আজ", "আজকে", "আজকের")):
        return today

    for pattern, date_format in (
        (r"\b(20\d{2}-\d{1,2}-\d{1,2})\b", "%Y-%m-%d"),
        (r"\b(\d{1,2}[/-]\d{1,2}[/-]20\d{2})\b", None),
    ):
        match = re.search(pattern, text)
        if not match:
            continue
        value = match.group(1)
        try:
            if date_format:
                return datetime.strptime(value, date_format).date()
            separator = "/" if "/" in value else "-"
            first, second, year = [int(part) for part in value.split(separator)]
            # Accept both DD/MM/YYYY and MM/DD/YYYY; prefer day-first if both are plausible.
            month, day = (second, first) if first > 12 else (first, second) if second > 12 else (second, first)
            return date(year, month, day)
        except ValueError:
            return None

    month_names = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7,
        "july": 7, "aug": 8, "august": 8, "sep": 9, "september": 9,
        "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
    }
    match = re.search(r"\b(\d{1,2})\s+([a-z]+)(?:\s+(20\d{2}))?\b", text)
    if match and match.group(2) in month_names:
        try:
            year = int(match.group(3) or today.year)
            result = date(year, month_names[match.group(2)], int(match.group(1)))
            if not match.group(3) and result < today:
                result = result.replace(year=today.year + 1)
            return result
        except ValueError:
            return None
    return None


def contains_date_reference(message):
    text = normalize_digits(message.lower())
    return bool(
        re.search(r"\b20\d{2}-\d{1,2}-\d{1,2}\b|\b\d{1,2}[/-]\d{1,2}[/-]20\d{2}\b", text)
        or re.search(r"\b\d{1,2}\s+(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\b", text)
        or any(word in text for word in ("today", "tomorrow", "day after tomorrow", "আজ", "কাল", "পরশু"))
    )


def detect_specialty(message):
    text = message.lower()
    for specialty, keywords in SPECIALTIES.items():
        if any(keyword in text for keyword in keywords):
            return specialty
    return None


def specialty_query(specialty):
    query = Q()
    for keyword in SPECIALTIES[specialty]:
        query |= Q(specialization__icontains=keyword) | Q(department__name__icontains=keyword)
    return query


def _doctor_payload(doctor, requested_date=None, with_slots=False, bangla=False):
    payload = {
        "id": doctor.pk,
        "name": doctor.user.get_full_name() or doctor.user.username,
        "specialization": doctor.specialization,
        "hospital": doctor.hospital.name if doctor.hospital else "",
        "department": doctor.department.name if doctor.department else "",
        "fee": str(doctor.consultation_fee),
        "date": requested_date.isoformat() if requested_date else "",
        "slots": [],
    }
    if requested_date and with_slots:
        slots = get_available_slots(doctor, requested_date)
        payload["slots"] = [
            {
                "start": slot["start_time"].strftime("%H:%M"),
                "end": slot["end_time"].strftime("%H:%M"),
                "booking_url": reverse("appointments:book", args=[doctor.pk]) + "?" + urlencode({
                    "date": requested_date.isoformat(),
                    "start_time": slot["start_time"].strftime("%H:%M"),
                    "end_time": slot["end_time"].strftime("%H:%M"),
                }),
            }
            for slot in slots[:8]
        ]
        if not payload["slots"]:
            payload["availability_message"] = "এই তারিখে আর খালি slot নেই। অন্য তারিখ চেষ্টা করুন।" if bangla else "No open slots remain for this date. Try another date."
    return payload


def _is_bangla(text):
    return any("\u0980" <= char <= "\u09ff" for char in text)


def find_available_doctors(requested_date, specialty=None, bangla=False):
    scheduled_user_ids = Schedule.objects.filter(
        date=requested_date,
        is_active=True,
        schedule_type=Schedule.ScheduleType.HOSPITAL_DUTY,
        user__role=Role.DOCTOR,
        user__is_active=True,
    ).values_list("user_id", flat=True).distinct()

    doctors = DoctorProfile.objects.filter(
        user_id__in=scheduled_user_ids,
        user__is_active=True,
    ).select_related("user", "hospital", "department")
    if specialty:
        doctors = doctors.filter(specialty_query(specialty))

    results = [_doctor_payload(doctor, requested_date, with_slots=True, bangla=bangla) for doctor in doctors.order_by("user__first_name", "user__last_name")[:30]]
    return results


def find_doctors(specialty=None):
    doctors = DoctorProfile.objects.filter(user__is_active=True).select_related("user", "hospital", "department")
    if specialty:
        doctors = doctors.filter(specialty_query(specialty))
    return [_doctor_payload(doctor) for doctor in doctors.order_by("user__first_name", "user__last_name")[:10]]


def get_patient_appointments(user):
    if not user or getattr(user, "role", None) != "PATIENT":
        return None
    today = timezone.localdate()
    return list(
        Appointment.objects.filter(
            patient=user,
            date__gte=today,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        ).select_related("doctor__user", "department").order_by("date", "start_time")[:5]
    )


def _appointment_reply(user, bangla):
    appointments = get_patient_appointments(user)
    if appointments is None:
        return "নিজের appointment দেখতে patient account দিয়ে লগইন করুন।" if bangla else "Please sign in with your patient account to view your own appointments."
    if not appointments:
        return "আপনার কোনো upcoming appointment নেই। চাইলে আজকের available doctor খুঁজে দিতে পারি।" if bangla else "You have no upcoming appointments. I can help find a doctor available today."
    lines = []
    for item in appointments:
        doctor_name = item.doctor.user.get_full_name() or item.doctor.user.username
        lines.append(f"{item.date:%d %b %Y} · {item.start_time:%H:%M} · Dr. {doctor_name} · {item.get_status_display()}")
    intro = "আপনার upcoming appointment:" if bangla else "Your upcoming appointments:"
    return intro + "\n" + "\n".join(lines)


def handle_message(message, user=None):
    text = message.strip()
    lowered = text.lower()
    bangla = _is_bangla(text)

    if not text:
        return {"reply": "Please type a message. আপনার কী সাহায্য দরকার?", "doctors": []}

    if any(keyword in lowered for keyword in EMERGENCY_KEYWORDS):
        return {
            "reply": (
                "This may need urgent attention. Please contact your local emergency service or go to the nearest emergency department now. I can't assess an emergency in chat.\n\nএটি জরুরি অবস্থা হতে পারে। এখনই স্থানীয় জরুরি সেবায় যোগাযোগ করুন বা নিকটস্থ হাসপাতালের জরুরি বিভাগে যান।"
            ),
            "doctors": [],
        }

    guided_result = handle_guided_message(text, user)
    if guided_result is not None:
        return guided_result

    if any(keyword in lowered for keyword in APPOINTMENT_KEYWORDS):
        return {"reply": _appointment_reply(user, bangla), "doctors": []}

    if any(word in lowered for word in ("hello", "hi", "হ্যালো", "সালাম", "assalamu")):
        return {
            "reply": "স্বাগতম! আজ/অন্য তারিখে কোন ডাক্তার আছেন, specialty অনুযায়ী doctor, অথবা আপনার appointment জানতে পারেন।" if bangla else "Welcome! Ask which doctors are available today or on another date, search by specialty, or check your appointments.",
            "doctors": [],
        }

    specialty = detect_specialty(text)
    requested_date = detect_date(text)
    availability_intent = any(keyword in lowered for keyword in AVAILABILITY_KEYWORDS)
    doctor_intent = any(keyword in lowered for keyword in DOCTOR_KEYWORDS)
    has_date_reference = contains_date_reference(text)

    if has_date_reference and requested_date is None:
        return {"reply": "তারিখটি বুঝতে পারিনি। তারিখ picker ব্যবহার করুন বা YYYY-MM-DD লিখুন; যেমন 2026-10-15." if bangla else "I couldn't read that date. Use the date picker or enter YYYY-MM-DD, for example 2026-10-15.", "doctors": []}

    if (requested_date and (availability_intent or doctor_intent or specialty)) or availability_intent:
        requested_date = requested_date or timezone.localdate()
        if requested_date < timezone.localdate():
            return {"reply": "তারিখটি পেরিয়ে গেছে। আজ বা ভবিষ্যতের তারিখ দিন।" if bangla else "That date has passed. Choose today or a future date.", "doctors": []}

        doctors = find_available_doctors(requested_date, specialty, bangla=bangla)
        if not doctors:
            if specialty:
                reply = f"{requested_date:%d %b %Y} তারিখে {specialty} বিভাগে কোনো doctor duty schedule-এ নেই। অন্য তারিখ বা specialty চেষ্টা করুন।" if bangla else f"No {specialty} doctor is scheduled on {requested_date:%d %b %Y}. Try another date or specialty."
            else:
                reply = f"{requested_date:%d %b %Y} তারিখে কোনো doctor-এর duty schedule পাওয়া যায়নি। অন্য তারিখ বেছে দেখুন।" if bangla else f"No doctor duty schedules were found for {requested_date:%d %b %Y}. Try another date."
            return {"reply": reply, "doctors": []}

        date_text = requested_date.strftime("%d %b %Y")
        reply = f"{date_text} তারিখে schedule-এ থাকা doctor-দের তালিকা দিলাম। খালি slot থাকলে Book চাপুন।" if bangla else f"Here are doctors scheduled for {date_text}. Choose an open slot and select Book."
        return {"reply": reply, "doctors": doctors}

    if specialty:
        doctors = find_doctors(specialty)
        if not doctors:
            reply = f"{specialty} বিভাগে doctor profile পাওয়া যায়নি। অন্য specialty লিখে দেখুন।" if bangla else f"I couldn't find a doctor matching {specialty}. Try another specialty."
            return {"reply": reply, "doctors": []}
        reply = f"{specialty} specialty-র doctor-দের profile দিলাম। নির্দিষ্ট দিনের availability দেখতে তারিখ লিখুন বা তারিখ picker ব্যবহার করুন।" if bangla else f"Here are doctors in {specialty}. Enter a date or use the date picker to check their availability."
        return {"reply": reply, "doctors": doctors}

    if doctor_intent:
        doctors = find_doctors()
        reply = "Project-এর doctor profile থেকে তালিকা দিলাম। কোনো দিনের schedule দেখতে তারিখও লিখুন।" if bangla else "Here are doctor profiles from MediCore. Include a date to check their schedules."
        return {"reply": reply if doctors else ("এখন কোনো doctor profile নেই।" if bangla else "There are no doctor profiles in MediCore yet."), "doctors": doctors}

    response = ai_reply(text)
    if response:
        return {"reply": response, "doctors": []}

    return {
        "reply": "আমি doctor, date অনুযায়ী schedule, available slot এবং আপনার appointment দেখতে পারি। উপরের option চাপুন বা নিজের প্রশ্ন লিখুন।" if bangla else "I can check doctors, date-based schedules, open appointment slots, and your appointments. Choose an option above or type your question.",
        "doctors": [],
    }
