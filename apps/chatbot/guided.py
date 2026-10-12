"""Database-backed answers for the chatbot's feature-by-feature question paths."""

from collections import Counter

from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.appointments.models import Appointment
from apps.billing.models import Bill, Payment
from apps.doctors.models import DoctorProfile
from apps.hospitals.models import Department, Hospital
from apps.medical_records.models import Consultation, LabTest, LabTestOrder, Prescription
from apps.notifications.models import Notification
from apps.nurses.models import HomeCareAvailability, HomeCareRequest, NurseProfile
from apps.pharmacy.models import DispensingRecord, Medicine
from apps.schedule_manager.models import Schedule

from .flows import get_start_options, get_submenu, option


PATIENT_ACTIONS = {
    "my_appointments", "medical_history", "patient_prescriptions", "patient_lab_reports",
    "patient_homecare", "patient_reviews", "find_nurse", "patient_bills", "patient_payments", "profile",
}
DOCTOR_ACTIONS = {"staff_appointments", "staff_schedule", "doctor_consultations", "doctor_prescriptions", "profile"}
NURSE_ACTIONS = {"nurse_requests", "staff_schedule", "nurse_availability", "profile"}
LAB_ACTIONS = {"lab_orders", "lab_catalog"}
PHARMACY_ACTIONS = {"pharmacy_queue", "medicine_stock", "dispensing_history"}
FRONTDESK_ACTIONS = {"frontdesk_appointments", "frontdesk_bills"}
ADMIN_ACTIONS = {"system_overview", "hospitals", "departments", "lab_orders", "frontdesk_appointments", "frontdesk_bills", "medicine_stock", "homecare_overview"}
REFERENCE_ACTIONS = {"hospitals", "departments"}


def _result(reply, options=None, links=None, doctors=None, date_picker=False):
    return {
        "reply": reply,
        "options": options or [option("← Main menu", "menu:start")],
        "links": links or [],
        "doctors": doctors or [],
        "date_picker": date_picker,
    }


def _link(label, route, **kwargs):
    return {"label": label, "url": reverse(route, kwargs=kwargs)}


def _localized(user, bangla, english):
    return bangla if getattr(user, "preferred_language", "") == "bn" else english


def _require(user, roles, feature):
    if user.role not in roles:
        return _result("এই feature আপনার account role-এ নেই। নিজের account-এর menu থেকে feature বেছে নিন।" if _is_bangla_user(user) else "That feature isn't available for your account role. Choose a feature from your own menu.")
    return None


def _is_bangla_user(user):
    return getattr(user, "language", "") == "bn"


def _format_appointment(appointment, show_patient=False):
    doctor_name = appointment.doctor.user.get_full_name() or appointment.doctor.user.username
    patient_part = f" · Patient {appointment.patient.public_id}" if show_patient else ""
    dept = appointment.department.name if appointment.department_id else ""
    return f"{appointment.date:%d %b %Y} {appointment.start_time:%H:%M} · Dr. {doctor_name}{patient_part} · {dept} · {appointment.get_status_display()}"


def _patient_appointments(user):
    appointments = Appointment.objects.filter(
        patient=user,
        date__gte=timezone.localdate(),
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
    ).select_related("doctor__user", "department").order_by("date", "start_time")[:8]
    return list(appointments)


def _patient_bills(user):
    return list(Bill.objects.filter(patient=user).order_by("-created_at")[:8])


def _bill_lines(bills):
    return [
        f"{bill.bill_id} · Total ৳{bill.total_amount} · Paid ৳{bill.paid_amount} · Due ৳{bill.total_amount - bill.paid_amount} · {bill.get_status_display()}"
        for bill in bills
    ]


def _profile_link(user):
    route_by_role = {
        Role.PATIENT: "patients:profile",
        Role.DOCTOR: "doctors:profile",
        Role.NURSE: "nurses:profile",
    }
    route = route_by_role.get(user.role)
    if route:
        return [_link("Open my profile", route)]
    if user.role == Role.ADMIN:
        return [_link("Open Django administration", "admin:index")]
    return []


def _action_response(action, user):
    today = timezone.localdate()

    if action in REFERENCE_ACTIONS:
        denied = _require(user, {Role.PATIENT, Role.ADMIN}, action)
        if denied:
            return denied
    elif action in PATIENT_ACTIONS:
        denied = _require(user, {Role.PATIENT}, action)
        if denied:
            return denied
    elif action in DOCTOR_ACTIONS:
        denied = _require(user, {Role.DOCTOR}, action)
        if denied:
            return denied
    elif action in NURSE_ACTIONS:
        denied = _require(user, {Role.NURSE}, action)
        if denied:
            return denied
    elif action in LAB_ACTIONS:
        denied = _require(user, {Role.LAB, Role.ADMIN}, action)
        if denied:
            return denied
    elif action in PHARMACY_ACTIONS:
        denied = _require(user, {Role.PHARMACIST, Role.ADMIN}, action)
        if denied:
            return denied
    elif action in FRONTDESK_ACTIONS:
        denied = _require(user, {Role.RECEPTIONIST, Role.ADMIN}, action)
        if denied:
            return denied
    elif action in ADMIN_ACTIONS:
        denied = _require(user, {Role.ADMIN}, action)
        if denied:
            return denied

    if action == "available_today":
        from .services import find_available_doctors

        doctors = find_available_doctors(today)
        reply = f"{today:%d %b %Y} তারিখে schedule-এ থাকা doctor-দের দেখুন। খালি slot থাকলে Book চাপুন." if doctors else f"আজ ({today:%d %b %Y}) কোনো doctor duty schedule-এ নেই। Doctor list বা অন্য date দেখুন।"
        return _result(reply, doctors=doctors, options=[option("Choose another date", "action:choose_date"), option("Find doctors", "action:browse_doctors"), option("← Main menu", "menu:start")])
    if action == "choose_date":
        return _result("যে তারিখে খুঁজবেন সেটি বেছে নিন। Schedule ও খালি slot MediCore data থেকে দেখানো হবে।", date_picker=True, options=[option("আজকের ডাক্তার", "action:available_today"), option("← Main menu", "menu:start")])
    if action == "browse_doctors":
        from .services import find_doctors

        doctors = find_doctors()
        links = [_link("Open doctor directory", "patients:find_doctors")]
        return _result(f"MediCore-এ {len(doctors)}টি doctor profile দেখাচ্ছি। তারিখ অনুযায়ী availability চাইলে একটি date দিন।", doctors=doctors, links=links, options=[option("Check today's availability", "action:available_today"), option("Choose a date", "action:choose_date"), option("← Main menu", "menu:start")])
    if action == "my_appointments":
        appointments = _patient_appointments(user)
        reply = "আপনার upcoming appointment নেই।" if not appointments else "আপনার upcoming appointment:\n" + "\n".join(_format_appointment(row) for row in appointments)
        return _result(reply, links=[_link("Open appointments", "patients:appointments")], options=[option("Find an available doctor", "menu:patient:appointments"), option("← Main menu", "menu:start")])
    if action == "appointment_help":
        if user.role in {Role.RECEPTIONIST, Role.ADMIN}:
            links = [_link("Open administration", "admin:index")] if user.role == Role.ADMIN else []
            return _result("Reception desk-এর appointment তালিকা chatbot-এ দেখুন। Chatbot appointment create বা cancel করে না; patient-এর booking পরিবর্তন করার option project-এ নেই।", links=links, options=[option("আজকের appointment", "action:frontdesk_appointments"), option("← Main menu", "menu:start")])
        return _result("ডাক্তার খুঁজুন → তারিখ ও খালি slot বেছে Book চাপুন → booking form জমা দিন। Cancel করতে My appointments page-এ appointment খুলুন। Chatbot নিজে appointment confirm করে না।", links=[_link("Find doctors", "patients:find_doctors"), _link("My appointments", "patients:appointments")], options=[option("Check today's doctors", "action:available_today"), option("← Main menu", "menu:start")])
    if action == "medical_history":
        rows = Consultation.objects.filter(patient=user).select_related("doctor", "appointment").order_by("-created_at")[:8]
        lines = [f"{row.appointment.date:%d %b %Y} · Dr. {row.doctor.get_full_name()} · {row.chief_complaint[:90]}" for row in rows]
        reply = "আপনার consultation history নেই।" if not lines else "আপনার সাম্প্রতিক consultation:\n" + "\n".join(lines)
        return _result(reply, links=[_link("Open medical history", "patients:medical_history")])
    if action == "patient_prescriptions":
        rows = Prescription.objects.filter(patient=user).prefetch_related("medicines").order_by("-created_at")[:8]
        lines = [f"{row.prescription_id} · {row.get_pharmacy_status_display()} · " + (", ".join(m.medicine_name for m in row.medicines.all()) or "No medicine listed") for row in rows]
        reply = "আপনার prescription নেই।" if not lines else "আপনার prescription:\n" + "\n".join(lines)
        return _result(reply, links=[_link("Open prescriptions", "patients:prescriptions")])
    if action == "patient_lab_reports":
        rows = LabTestOrder.objects.filter(patient=user).select_related("test").order_by("-created_at")[:8]
        lines = [f"{row.order_id} · {row.test.name} · {row.get_status_display()}" + (f" · Result: {row.result[:100]}" if row.result and row.status == LabTestOrder.Status.COMPLETED else "") for row in rows]
        reply = "আপনার lab order/report নেই।" if not lines else "আপনার সাম্প্রতিক lab report/order:\n" + "\n".join(lines)
        return _result(reply, links=[_link("Open lab reports", "patients:lab_reports")])
    if action == "patient_homecare":
        rows = HomeCareRequest.objects.filter(patient=user).select_related("nurse__user").order_by("-date", "-start_time")[:8]
        lines = [f"{row.date:%d %b %Y} {row.start_time:%H:%M} · {row.nurse.user.get_full_name()} · {row.get_status_display()}" for row in rows]
        reply = "আপনার home-care request নেই।" if not lines else "আপনার home-care request:\n" + "\n".join(lines)
        return _result(reply, links=[_link("Open my home-care requests", "nurses:my_home_care_requests")], options=[option("Find a nurse", "action:find_nurse"), option("← Main menu", "menu:start")])
    if action == "patient_reviews":
        requests = list(HomeCareRequest.objects.filter(patient=user, status=HomeCareRequest.Status.COMPLETED).select_related("nurse__user").order_by("-date")[:10])
        reviewed_ids = set(HomeCareRequest.objects.filter(pk__in=[row.pk for row in requests], review__isnull=False).values_list("pk", flat=True)) if requests else set()
        lines = [f"{row.date:%d %b %Y} · {row.nurse.user.get_full_name()} · {'Review submitted' if row.pk in reviewed_ids else 'Review available'}" for row in requests]
        links = []
        first_unreviewed = next((row for row in requests if row.pk not in reviewed_ids), None)
        if first_unreviewed:
            links.append(_link("Review a completed request", "nurses:create_review", request_id=first_unreviewed.pk))
        return _result("Completed home-care requests:\n" + ("\n".join(lines) if lines else "আপনার completed home-care request নেই।"), links=links, options=[option("My home-care requests", "action:patient_homecare"), option("← Main menu", "menu:start")])
    if action == "find_nurse":
        denied = _require(user, {Role.PATIENT}, action)
        if denied:
            return denied
        nurses = NurseProfile.objects.filter(user__is_active=True, is_verified=True).select_related("user", "hospital").prefetch_related("home_care_availability").order_by("-rating", "user__first_name")[:10]
        rows = []
        links = []
        for nurse in nurses:
            availability = ", ".join(f"{slot.get_day_display()} {slot.start_time:%H:%M}-{slot.end_time:%H:%M}" for slot in nurse.home_care_availability.filter(is_active=True)[:3])
            rows.append(f"{nurse.user.get_full_name()} · {nurse.hospital.name if nurse.hospital else 'Hospital not listed'} · Rating {nurse.rating}/5 · {availability or nurse.skills[:80]}")
            links.append(_link(f"Request home care: {nurse.user.get_full_name()}", "nurses:request_home_care", nurse_id=nurse.pk))
        reply = "এখন verified nurse profile নেই।" if not rows else "MediCore-এর verified nurse:\n" + "\n".join(rows)
        return _result(reply, links=links, options=[option("My home-care requests", "action:patient_homecare"), option("← Main menu", "menu:start")])
    if action == "homecare_help":
        return _result("Nurse বেছে request form-এ date, time ও প্রয়োজনীয় তথ্য দিন। Nurse availability এবং schedule মিলিয়ে request পাঠানো হয়; request-এর status My home-care page-এ দেখা যাবে।", links=[_link("My home-care requests", "nurses:my_home_care_requests")], options=[option("Find a nurse", "action:find_nurse"), option("← Main menu", "menu:start")])
    if action in {"patient_bills", "patient_payments"}:
        bills = _patient_bills(user)
        if action == "patient_payments":
            payments = Payment.objects.filter(bill__patient=user).select_related("bill").order_by("-paid_at")[:10]
            lines = [f"{row.bill.bill_id} · ৳{row.amount} · {row.get_method_display()} · {row.paid_at:%d %b %Y}" for row in payments]
            reply = "আপনার payment record নেই।" if not lines else "আপনার payment history:\n" + "\n".join(lines)
        else:
            lines = _bill_lines(bills)
            reply = "আপনার bill নেই।" if not lines else "আপনার bill ও বকেয়া:\n" + "\n".join(lines)
        links = [_link("Open latest bill", "billing:bill_detail", bill_id=bills[0].pk)] if bills else []
        return _result(reply, links=links, options=[option("How to pay", "action:payment_help"), option("← Main menu", "menu:start")])
    if action == "payment_help":
        if user.role in {Role.RECEPTIONIST, Role.ADMIN}:
            link = _link("Open bills", "billing:bills") if user.role == Role.RECEPTIONIST else _link("Open administration", "admin:index")
            return _result("Bill detail খুলে due balance যাচাই করুন, তারপর Record payment ব্যবহার করুন। Chatbot payment জমা বা bill পরিবর্তন করে না।", links=[link], options=[option("Recent bills", "action:frontdesk_bills"), option("← Main menu", "menu:start")])
        bills = _patient_bills(user) if user.role == Role.PATIENT else []
        links = [_link("Open latest bill", "billing:bill_detail", bill_id=bills[0].pk)] if bills else []
        return _result("আপনার bill-এর detail খুলে due amount দেখুন। Payment জমা দেওয়ার ব্যবস্থা Reception/Admin করে; Chatbot payment বা bill পরিবর্তন করে না।", links=links, options=[option("My payment status", "action:patient_payments"), option("← Main menu", "menu:start")])
    if action == "hospitals":
        rows = Hospital.objects.filter(is_active=True).order_by("name")[:20]
        lines = [f"{row.name} · {row.address}" for row in rows]
        links = [_link("Browse doctors", "patients:find_doctors")] if user.role == Role.PATIENT else ([_link("Open administration", "admin:index")] if user.role == Role.ADMIN else [])
        return _result("MediCore-এর active hospital:\n" + "\n".join(lines) if lines else "কোনো active hospital record নেই।", links=links)
    if action == "departments":
        rows = Department.objects.filter(is_active=True, hospital__is_active=True).select_related("hospital").order_by("hospital__name", "name")[:30]
        lines = [f"{row.name} · {row.hospital.name}" for row in rows]
        links = [_link("Browse doctors", "patients:find_doctors")] if user.role == Role.PATIENT else ([_link("Open administration", "admin:index")] if user.role == Role.ADMIN else [])
        return _result("Departments ও specialty:\n" + "\n".join(lines) if lines else "কোনো active department record নেই।", links=links)
    if action == "notifications":
        all_notes = Notification.objects.filter(recipient=user)
        unread = all_notes.filter(is_read=False).count()
        recent = all_notes.order_by("-created_at")[:5]
        lines = [f"{n.title} · {n.created_at:%d %b %Y} · {'Unread' if not n.is_read else 'Read'}" for n in recent]
        reply = f"আপনার unread notification: {unread}.\n" + ("\n".join(lines) if lines else "কোনো notification নেই।")
        return _result(reply, links=[_link("Open notifications", "notifications:list")])
    if action == "profile":
        return _result("নিজের profile বা account তথ্য দেখতে project-এর profile page খুলুন। Password ভুলে গেলে sign-in page-এর password reset ব্যবহার করুন.", links=_profile_link(user), options=[option("Password reset help", "action:account_help"), option("← Main menu", "menu:start")])
    if action == "account_help":
        return _result("Password পরিবর্তন বা reset করতে Sign in page থেকে Forgot password বেছে নিন। Chatbot কখনো password চাইবে না।", links=[_link("Sign in / password reset", "login")])
    if action == "general_health":
        return _result("আপনার সাধারণ health question লিখুন। আমি সাধারণ তথ্য দিতে পারি, কিন্তু diagnosis বা prescription দিতে পারি না। জরুরি হলে এখনই স্থানীয় emergency service-এ যোগাযোগ করুন।", options=[option("Doctor & appointments", "menu:patient:appointments"), option("← Main menu", "menu:start")])

    if action == "staff_appointments":
        rows = Appointment.objects.filter(doctor__user=user, date__gte=today).exclude(status__in=[Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW]).select_related("patient", "doctor__user", "department").order_by("date", "start_time")[:10]
        lines = [_format_appointment(row, show_patient=True) for row in rows]
        return _result("আপনার upcoming appointment:\n" + "\n".join(lines) if lines else "আপনার upcoming appointment নেই।", links=[_link("Open doctor appointments", "doctors:appointments")])
    if action == "staff_schedule":
        rows = Schedule.objects.filter(user=user, is_active=True, date__gte=today).select_related("hospital", "department").order_by("date", "start_time")[:10]
        lines = [f"{row.date:%d %b %Y} {row.start_time:%H:%M}–{row.end_time:%H:%M} · {row.get_schedule_type_display()} · {row.hospital.name if row.hospital else 'No hospital'}" for row in rows]
        route = "schedule_manager:list"
        return _result("আপনার upcoming schedule:\n" + "\n".join(lines) if lines else "আপনার upcoming schedule নেই।", links=[_link("Open my schedule", route)])
    if action == "doctor_consultations":
        rows = Consultation.objects.filter(doctor=user).select_related("patient", "appointment").order_by("-created_at")[:8]
        lines = [f"{row.appointment.date:%d %b %Y} · Patient {row.patient.public_id} · {row.chief_complaint[:80]}" for row in rows]
        return _result("আপনার সাম্প্রতিক consultation:\n" + "\n".join(lines) if lines else "আপনার consultation record নেই।", links=[_link("Open appointments", "doctors:appointments")])
    if action == "doctor_prescriptions":
        rows = Prescription.objects.filter(doctor=user).select_related("consultation__appointment").order_by("-created_at")[:8]
        lines = [f"{row.prescription_id} · {row.consultation.appointment.date:%d %b %Y} · {row.get_pharmacy_status_display()}" for row in rows]
        return _result("আপনার recent prescription:\n" + "\n".join(lines) if lines else "আপনার prescription record নেই।", links=[_link("Open appointments", "doctors:appointments")])
    if action == "nurse_requests":
        rows = HomeCareRequest.objects.filter(nurse__user=user).exclude(status__in=[HomeCareRequest.Status.CANCELLED, HomeCareRequest.Status.REJECTED]).select_related("patient").order_by("date", "start_time")[:10]
        lines = [f"{row.date:%d %b %Y} {row.start_time:%H:%M} · Patient {row.patient.public_id} · {row.get_status_display()}" for row in rows]
        return _result("আপনার home-care request:\n" + "\n".join(lines) if lines else "আপনার কাছে home-care request নেই।", links=[_link("Open care requests", "nurses:nurse_requests")])
    if action == "nurse_availability":
        rows = HomeCareAvailability.objects.filter(nurse__user=user, is_active=True).order_by("day", "start_time")
        lines = [f"{row.get_day_display()} · {row.start_time:%H:%M}–{row.end_time:%H:%M}" for row in rows]
        return _result("আপনার home-care availability:\n" + "\n".join(lines) if lines else "আপনার active availability set করা নেই।", links=[_link("Open my profile", "nurses:profile"), _link("Open my schedule", "schedule_manager:list")])
    if action == "nurse_request_help":
        return _result("Home-care request খুলে patient-এর প্রয়োজন, date ও time যাচাই করুন; এরপর request-এর status update করুন। Availability বা schedule conflict থাকলে আগে সেটি মিলিয়ে নিন।", links=[_link("Open my care requests", "nurses:nurse_requests")], options=[option("আমার request দেখুন", "action:nurse_requests"), option("← Main menu", "menu:start")])
    if action == "lab_orders":
        rows = LabTestOrder.objects.select_related("test").order_by("-created_at")[:10]
        counts = Counter(LabTestOrder.objects.values_list("status", flat=True))
        count_line = " · ".join(f"{label}: {count}" for label, count in sorted(counts.items())) or "No orders"
        lines = [f"{row.order_id} · {row.test.name} · {row.get_status_display()}" for row in rows]
        link = _link("Open lab orders", "medical_records:lab_orders") if user.role == Role.LAB else _link("Open administration", "admin:index")
        return _result(f"Lab order status: {count_line}\n" + ("\n".join(lines) if lines else "No lab orders."), links=[link])
    if action == "lab_catalog":
        rows = LabTest.objects.filter(is_active=True).order_by("name")[:20]
        lines = [f"{row.name} · {row.code}" for row in rows]
        return _result("Active lab tests:\n" + "\n".join(lines) if lines else "No active lab tests.", links=[_link("Open lab orders", "medical_records:lab_orders")])
    if action == "pharmacy_queue":
        rows = Prescription.objects.select_related("patient").prefetch_related("medicines").exclude(pharmacy_status=Prescription.PharmacyStatus.DISPENSED).order_by("created_at")[:10]
        lines = [f"{row.prescription_id} · Patient {row.patient.public_id} · {row.get_pharmacy_status_display()}" for row in rows]
        return _result("Prescription queue:\n" + "\n".join(lines) if lines else "No prescription is waiting to be dispensed.", links=[_link("Open pharmacy prescriptions", "pharmacy:prescriptions")])
    if action == "medicine_stock":
        rows = Medicine.objects.filter(is_active=True).order_by("stock_quantity", "name")[:15]
        lines = [f"{row.name} {row.strength} · Stock {row.stock_quantity} {row.unit} · {'LOW' if row.stock_quantity <= row.reorder_level else 'OK'}" for row in rows]
        link = _link("Open pharmacy", "pharmacy:prescriptions") if user.role == Role.PHARMACIST else _link("Open administration", "admin:index")
        return _result("Medicine inventory from MediCore:\n" + "\n".join(lines) if lines else "No active medicine inventory.", links=[link])
    if action == "dispensing_history":
        rows = DispensingRecord.objects.filter(pharmacist=user).select_related("prescription", "medicine").order_by("-dispensed_at")[:10]
        lines = [f"{row.prescription.prescription_id} · {row.medicine.name} × {row.quantity} · {row.get_status_display()}" for row in rows]
        return _result("Your recent dispensing records:\n" + "\n".join(lines) if lines else "No dispensing records for your account.", links=[_link("Open prescriptions", "pharmacy:prescriptions")])
    if action in {"frontdesk_appointments", "frontdesk_bills"}:
        if action == "frontdesk_appointments":
            rows = Appointment.objects.filter(date__gte=today).exclude(status__in=[Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW]).select_related("patient", "doctor__user", "department").order_by("date", "start_time")[:12]
            lines = [_format_appointment(row, show_patient=True) for row in rows]
            links = [_link("Open administration", "admin:index")] if user.role == Role.ADMIN else []
            return _result("Upcoming appointment desk:\n" + "\n".join(lines) if lines else "No upcoming appointments.", links=links)
        bills = list(Bill.objects.select_related("patient").exclude(status=Bill.Status.CANCELLED).order_by("-created_at")[:10])
        link = _link("Open bills", "billing:bills") if user.role == Role.RECEPTIONIST else _link("Open administration", "admin:index")
        return _result("Recent bills:\n" + ("\n".join(f"{bill.bill_id} · Patient {bill.patient.public_id} · ৳{bill.total_amount} · Due ৳{bill.total_amount - bill.paid_amount} · {bill.get_status_display()}" for bill in bills) if bills else "No bills found."), links=[link])
    if action == "system_overview":
        role_counts = User.objects.values_list("role", flat=True)
        roles = Counter(role_counts)
        summary = [f"Users {User.objects.count()} · Doctors {DoctorProfile.objects.count()} · Nurses {NurseProfile.objects.count()}", f"Hospitals {Hospital.objects.count()} · Departments {Department.objects.count()} · Appointments {Appointment.objects.count()}", f"Consultations {Consultation.objects.count()} · Lab orders {LabTestOrder.objects.count()} · Bills {Bill.objects.count()}", f"Home-care requests {HomeCareRequest.objects.count()} · Pharmacy items {Medicine.objects.count()}", "Users by role: " + ", ".join(f"{role} {count}" for role, count in sorted(roles.items()))]
        return _result("MediCore system overview (live database counts):\n" + "\n".join(summary), links=[_link("Open administration", "admin:index")])
    if action == "homecare_overview":
        counts = Counter(HomeCareRequest.objects.values_list("status", flat=True))
        lines = [f"{status}: {count}" for status, count in sorted(counts.items())]
        return _result("Home-care request counts:\n" + ("\n".join(lines) if lines else "No home-care requests."), links=[_link("Open administration", "admin:index")])

    return _result("এই option-টি এখনও configure করা হয়নি। Main menu থেকে অন্য feature বেছে নিন।")


def handle_guided_message(message, user):
    """Handle menu tokens and feature wording; return None for normal chat queries."""
    if user is None:
        return None
    text = message.strip()
    if text == "menu:start":
        return _result("আপনার কোন feature নিয়ে সাহায্য দরকার? একটি topic বেছে নিন:", options=get_start_options(user.role))

    if text.startswith("menu:"):
        parts = text.split(":", 2)
        if len(parts) != 3 or parts[1] != user.role.lower():
            return _result("আপনার account-এর menu থেকে feature বেছে নিন।", options=get_start_options(user.role))
        submenu = get_submenu(f"{parts[1]}:{parts[2]}")
        if submenu is None:
            return _result("এই feature menu-টি পাওয়া যায়নি। Main menu থেকে বেছে নিন।", options=get_start_options(user.role))
        return _result("এই feature-এ কোন বিষয়টি জানতে চান?", options=submenu + [option("← Main menu", "menu:start")])

    if text.startswith("action:"):
        return _action_response(text.split(":", 1)[1], user)

    lower = text.lower()
    bangla_route = any("\u0980" <= char <= "\u09ff" for char in text)
    appointment_action = {
        Role.PATIENT: "my_appointments",
        Role.DOCTOR: "staff_appointments",
        Role.RECEPTIONIST: "frontdesk_appointments",
        Role.ADMIN: "frontdesk_appointments",
    }.get(user.role)
    prescription_action = {
        Role.PATIENT: "patient_prescriptions",
        Role.DOCTOR: "doctor_prescriptions",
        Role.PHARMACIST: "pharmacy_queue",
        Role.ADMIN: "pharmacy_queue",
    }.get(user.role)
    lab_action = {
        Role.PATIENT: "patient_lab_reports",
        Role.LAB: "lab_orders",
        Role.ADMIN: "lab_orders",
    }.get(user.role)
    homecare_action = {
        Role.PATIENT: "patient_homecare",
        Role.NURSE: "nurse_requests",
        Role.ADMIN: "homecare_overview",
    }.get(user.role)
    bill_action = {
        Role.PATIENT: "patient_bills",
        Role.RECEPTIONIST: "frontdesk_bills",
        Role.ADMIN: "frontdesk_bills",
    }.get(user.role)
    intents = [
        (("my appointment", "আমার appointment", "আমার অ্যাপয়েন্টমেন্ট", "আমার অ্যাপয়েন্টমেন্ট"), appointment_action),
        (("medical history", "consultation history", "মেডিকেল হিস্ট্রি", "চিকিৎসার ইতিহাস"), "medical_history"),
        (("my prescription", "prescriptions", "প্রেসক্রিপশন"), prescription_action),
        (("my lab", "lab report", "test result", "ল্যাব রিপোর্ট", "পরীক্ষার রিপোর্ট"), lab_action),
        (("home care request", "my home care", "homecare", "হোম কেয়ার", "হোম কেয়ার", "আমার নার্স"), homecare_action),
        (("my bill", "my payment", "bill status", "আমার বিল", "আমার পেমেন্ট"), bill_action),
        (("notification", "নোটিফিকেশন", "বার্তা"), "notifications"),
        (("my profile", "আমার প্রোফাইল", "profile"), "profile"),
        (("my schedule", "আমার schedule", "আমার সময়সূচি"), "staff_schedule"),
        (("medicine stock", "inventory", "ওষুধের stock", "ওষুধের মজুদ"), "medicine_stock"),
        (("hospital list", "হাসপাতালের তালিকা"), "hospitals"),
        (("department list", "specialty list", "বিভাগের তালিকা"), "departments"),
    ]
    for keywords, action in intents:
        if action and any(keyword in lower for keyword in keywords):
            result = _action_response(action, user)
            if bangla_route and result.get("reply"):
                result["reply"] = result["reply"].replace("Your", "আপনার")
            return result
    return None
