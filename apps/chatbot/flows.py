"""Role-aware guided question paths for the MediCore assistant."""


def option(label, value):
    return {"label": label, "value": value}


START_MENUS = {
    "PATIENT": [
        option("🩺 ডাক্তার ও appointment", "menu:patient:appointments"),
        option("📋 আমার medical record", "menu:patient:records"),
        option("🏠 Nurse ও home care", "menu:patient:homecare"),
        option("💳 Bill ও payment", "menu:patient:billing"),
        option("🏥 Hospital ও department", "menu:patient:hospitals"),
        option("🔔 Notification", "action:notifications"),
        option("👤 আমার account", "menu:patient:account"),
        option("💬 সাধারণ health question", "action:general_health"),
    ],
    "DOCTOR": [
        option("📅 আমার appointment", "action:staff_appointments"),
        option("🗓️ আমার schedule", "action:staff_schedule"),
        option("🩺 আমার consultation", "action:doctor_consultations"),
        option("💊 আমার prescription", "action:doctor_prescriptions"),
        option("👤 আমার profile", "action:profile"),
        option("🔔 Notification", "action:notifications"),
    ],
    "NURSE": [
        option("🏠 Home-care request", "menu:nurse:homecare"),
        option("🗓️ আমার schedule", "action:staff_schedule"),
        option("⏰ আমার availability", "action:nurse_availability"),
        option("👤 আমার profile", "action:profile"),
        option("🔔 Notification", "action:notifications"),
    ],
    "LAB": [
        option("🧪 Lab order", "action:lab_orders"),
        option("📚 Test catalogue", "action:lab_catalog"),
        option("🔔 Notification", "action:notifications"),
    ],
    "PHARMACIST": [
        option("💊 Prescription queue", "action:pharmacy_queue"),
        option("📦 Medicine stock", "action:medicine_stock"),
        option("🧾 আমার dispensing record", "action:dispensing_history"),
        option("🔔 Notification", "action:notifications"),
    ],
    "RECEPTIONIST": [
        option("📅 Appointment", "menu:reception:appointments"),
        option("💳 Billing ও payment", "menu:reception:billing"),
        option("🔔 Notification", "action:notifications"),
    ],
    "ADMIN": [
        option("📊 System overview", "action:system_overview"),
        option("🏥 Hospitals & departments", "action:hospitals"),
        option("📅 Appointments", "action:frontdesk_appointments"),
        option("🧪 Lab orders", "action:lab_orders"),
        option("💳 Billing", "action:frontdesk_bills"),
        option("💊 Pharmacy stock", "action:medicine_stock"),
        option("🏠 Home-care requests", "action:homecare_overview"),
        option("🔔 Notifications", "action:notifications"),
    ],
}


SUB_MENUS = {
    "patient:appointments": [
        option("ডাক্তার খুঁজুন · Find doctors", "action:browse_doctors"),
        option("আজ কারা আছেন? · Available today", "action:available_today"),
        option("অন্য তারিখ দেখুন · Choose date", "action:choose_date"),
        option("আমার appointment · My appointments", "action:my_appointments"),
        option("Book বা cancel কীভাবে? · Help", "action:appointment_help"),
    ],
    "patient:records": [
        option("চিকিৎসার ইতিহাস · Consultation history", "action:medical_history"),
        option("আমার prescription · Prescriptions", "action:patient_prescriptions"),
        option("আমার lab report · Lab reports", "action:patient_lab_reports"),
    ],
    "patient:homecare": [
        option("Nurse খুঁজুন · Find a nurse", "action:find_nurse"),
        option("আমার home-care request", "action:patient_homecare"),
        option("Review দেখুন বা দিন · Reviews", "action:patient_reviews"),
        option("Home care কীভাবে কাজ করে?", "action:homecare_help"),
    ],
    "patient:billing": [
        option("আমার bill ও বকেয়া · Bills", "action:patient_bills"),
        option("Payment history", "action:patient_payments"),
        option("Bill কীভাবে pay করব?", "action:payment_help"),
    ],
    "patient:hospitals": [
        option("MediCore-এর hospital", "action:hospitals"),
        option("Department ও specialty", "action:departments"),
    ],
    "patient:account": [
        option("আমার profile দেখুন", "action:profile"),
        option("Password change বা reset", "action:account_help"),
    ],
    "nurse:homecare": [
        option("আমাকে দেওয়া request", "action:nurse_requests"),
        option("আমার availability", "action:nurse_availability"),
        option("Request update করব কীভাবে?", "action:nurse_request_help"),
    ],
    "reception:appointments": [
        option("আজকের appointment", "action:frontdesk_appointments"),
        option("Appointment desk help", "action:appointment_help"),
    ],
    "reception:billing": [
        option("Bill ও payment status", "action:frontdesk_bills"),
        option("Payment record করব", "action:payment_help"),
    ],
}


def get_start_options(role):
    return START_MENUS.get(role, START_MENUS["PATIENT"])


def get_submenu(path):
    return SUB_MENUS.get(path)
