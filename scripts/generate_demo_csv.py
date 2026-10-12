"""Generate the fictional, relational MediCore demo dataset CSV."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "medicore_demo_data.csv"
FIELDS = ["feature", "key", "ref1", "ref2", "ref3", "payload_json"]
rows = []


def add(feature, key, ref1="", ref2="", ref3="", **payload):
    rows.append({
        "feature": feature,
        "key": key,
        "ref1": ref1,
        "ref2": ref2,
        "ref3": ref3,
        "payload_json": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    })


specialties = [
    ("CARD", "Cardiology", "Heart health"),
    ("DERM", "Dermatology", "Skin health"),
    ("PEDI", "Pediatrics", "Child health"),
    ("ORTH", "Orthopedics", "Bone and joint health"),
    ("NEUR", "Neurology", "Nervous system health"),
    ("ENT", "ENT", "Ear, nose and throat care"),
    ("GAST", "Gastroenterology", "Digestive health"),
    ("OPHT", "Ophthalmology", "Eye health"),
    ("ENDO", "Endocrinology", "Hormone health"),
    ("GEN", "General Medicine", "General health consultation"),
]
doctor_names = ["Amina Rahman", "Farhan Ahmed", "Nusrat Jahan", "Imran Hossain", "Sadia Karim", "Tanvir Islam", "Maliha Chowdhury", "Rafiq Hasan", "Samira Akter", "Nabil Khan"]
nurse_names = ["Rupa Sultana", "Shafiq Alam", "Mitu Das", "Jamal Uddin", "Lamia Noor", "Sabbir Hossain", "Tania Islam", "Rasheda Begum", "Nayeem Kabir", "Purnima Roy"]
patient_names = ["Anika Demo", "Rahim Sample", "Maya Example", "Sohan Test", "Nadia Sample", "Arif Demo", "Tithi Example", "Hasan Test", "Rima Sample", "Omar Demo"]
lab_names = ["Lab Staff 01", "Lab Staff 02", "Lab Staff 03", "Lab Staff 04", "Lab Staff 05", "Lab Staff 06", "Lab Staff 07", "Lab Staff 08", "Lab Staff 09", "Lab Staff 10"]
pharmacist_names = ["Pharmacist 01", "Pharmacist 02", "Pharmacist 03", "Pharmacist 04", "Pharmacist 05", "Pharmacist 06", "Pharmacist 07", "Pharmacist 08", "Pharmacist 09", "Pharmacist 10"]
receptionist_names = ["Reception 01", "Reception 02", "Reception 03", "Reception 04", "Reception 05", "Reception 06", "Reception 07", "Reception 08", "Reception 09", "Reception 10"]


def account(role, number, name):
    first, *rest = name.split()
    username = f"demo_{role.lower()}_{number:02d}"
    add("user", username, role=role.upper(), first_name=first, last_name=" ".join(rest), email=f"{username}@example.test", is_active=True, is_verified=True)
    return username


for i, (code, dept, description) in enumerate(specialties, 1):
    hospital_code = f"HOSP-{i:02d}"
    add("hospital", hospital_code, name=f"MediCore Demo Clinic {i:02d}", address=f"Demo Road {i:02d}, Dhaka", phone=f"+880-000-000-{i:04d}", email=f"clinic{i:02d}@example.test", description="Fictional sample hospital for local software demonstration.", is_active=True)
    add("department", f"DEPT-{code}", hospital_code, name=dept, description=description, is_active=True)

for i, name in enumerate(patient_names, 1):
    username = account("patient", i, name)
    add("patient_profile", username, date_of_birth=f"199{i % 10}-0{(i % 9) + 1}-15", gender=["FEMALE", "MALE", "OTHER"][i % 3], phone=f"+880-000-100-{i:04d}", address=f"Demo Address {i:02d}, Dhaka", blood_group=["A+", "B+", "O+", "AB+"][i % 4], emergency_contact=f"Demo Contact {i:02d}", emergency_contact_phone=f"+880-000-200-{i:04d}")

doctor_users = []
nurse_users = []
lab_users = []
pharmacist_users = []
reception_users = []
for i, name in enumerate(doctor_names, 1):
    username = account("doctor", i, name)
    doctor_users.append(username)
    code, dept, _ = specialties[i - 1]
    add("doctor_profile", username, f"HOSP-{i:02d}", f"DEPT-{code}", specialization=dept, qualification="MBBS, FCPS (Demo)", experience_years=5 + i, license_number=f"DEMO-DOC-{i:04d}", phone=f"+880-000-300-{i:04d}", bio="Fictional demo profile. Not a real clinician.", consultation_fee=800 + i * 100)
for i, name in enumerate(nurse_names, 1):
    username = account("nurse", i, name)
    nurse_users.append(username)
    add("nurse_profile", username, f"HOSP-{i:02d}", qualification="Diploma in Nursing (Demo)", experience_years=2 + i, skills="Patient support; basic care; sample profile", phone=f"+880-000-400-{i:04d}", bio="Fictional demo profile. Not a real care provider.", is_verified=True, rating=f"{4 + (i % 10) / 10:.2f}", total_reviews=i)
for collection, names, role, dest in [
    ("lab", lab_names, "lab", lab_users),
    ("pharmacist", pharmacist_names, "pharmacist", pharmacist_users),
    ("receptionist", receptionist_names, "receptionist", reception_users),
]:
    for i, name in enumerate(names, 1):
        dest.append(account(role, i, name))

days = ["SATURDAY", "SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
for i, username in enumerate(nurse_users, 1):
    add("homecare_availability", f"AVAIL-{i:02d}", username, day=days[(i - 1) % 7], start_time="08:00", end_time="16:00", is_active=True, notes="Fictional demo availability.")

for i, username in enumerate(doctor_users, 1):
    code, _, _ = specialties[i - 1]
    add("schedule", f"DOC-SCHED-{i:02d}", username, f"HOSP-{i:02d}", f"DEPT-{code}", date=f"today+{i}d", start_time="09:00", end_time="17:00", schedule_type="HOSPITAL_DUTY", is_active=True, notes="Sample doctor duty schedule.")
for i, username in enumerate(nurse_users, 1):
    add("schedule", f"NUR-SCHED-{i:02d}", username, date=f"today+{i}d", start_time="08:00", end_time="16:00", schedule_type="HOME_CARE", is_active=True, notes="Sample nurse home-care schedule.")

for i, username in enumerate(doctor_users, 1):
    code, dept, _ = specialties[i - 1]
    add("appointment", f"APPT-PAST-{i:02d}", f"demo_patient_{i:02d}", username, f"DEPT-{code}", date=f"today-{i}d", start_time="10:00", end_time="10:30", status="COMPLETED", reason="Routine demo consultation", notes="Fictional sample appointment.")
    add("appointment", f"APPT-NEXT-{i:02d}", f"demo_patient_{i:02d}", username, f"DEPT-{code}", date=f"today+{i}d", start_time="11:00", end_time="11:30", status="CONFIRMED" if i % 2 else "PENDING", reason="Follow-up demo booking", notes="Fictional sample appointment.")

complaints = ["Routine wellness discussion", "Mild seasonal discomfort", "General follow-up", "Preventive care discussion", "Recurring mild headache", "Skin care question", "Digestive discomfort", "Joint comfort follow-up", "Sleep routine discussion", "General health review"]
for i in range(1, 11):
    add("consultation", f"CONS-{i:02d}", f"APPT-PAST-{i:02d}", chief_complaint=complaints[i - 1], symptoms="Fictional sample symptoms only.", diagnosis="Demo record: assessment deferred to qualified clinician.", clinical_notes="Synthetic training data. Not for diagnosis or treatment.", follow_up_date=f"today+{i + 14}d")

for i in range(1, 11):
    add("prescription", f"RX-DEMO-{i:02d}", f"CONS-{i:02d}", pharmacy_status="DISPENSED" if i % 2 else "PARTIALLY_DISPENSED", advice="Demo-only prescription example. Do not use for medical care.", tests_advised="See linked demo lab order.", follow_up_date=f"today+{i + 14}d")
    add("prescription_medicine", f"RXMED-{i:02d}-A", f"RX-DEMO-{i:02d}", medicine_name=f"Demo Medicine {i:02d}", dosage="1 unit (sample)", frequency="As directed by clinician (sample)", duration="5 days (sample)", instructions="Fictional dataset only; not a medical recommendation.")
    add("prescription_medicine", f"RXMED-{i:02d}-B", f"RX-DEMO-{i:02d}", medicine_name=f"Demo Supplement {i:02d}", dosage="1 unit (sample)", frequency="Once daily (sample)", duration="3 days (sample)", instructions="Fictional dataset only; not a medical recommendation.")

test_names = ["Demo CBC Panel", "Demo Blood Glucose", "Demo Lipid Panel", "Demo Thyroid Panel", "Demo Vitamin Panel", "Demo Urine Analysis", "Demo Liver Panel", "Demo Kidney Panel", "Demo ECG Entry", "Demo Imaging Review"]
for i, name in enumerate(test_names, 1):
    add("lab_test", f"TEST-{i:02d}", name=name, code=f"DEMO-LAB-{i:02d}", description="Fictional catalogue entry for software testing.", is_active=True)
    add("lab_order", f"LAB-ORDER-{i:02d}", f"CONS-{i:02d}", f"TEST-{i:02d}", status=["COMPLETED", "PROCESSING", "SAMPLE_COLLECTED", "REQUESTED"][i % 4], result="Demo-only result placeholder. Not for diagnosis." if i % 4 == 0 else "", notes="Synthetic sample lab order.")

for i in range(1, 11):
    add("medicine", f"MED-{i:02d}", name=f"Demo Medicine {i:02d}", generic_name=f"Example Compound {i:02d}", strength="Sample 100 mg", unit="tablet", stock_quantity=100 + i, reorder_level=10, expiry_date="today+365d", is_active=True)
    add("dispensing", f"DISP-{i:02d}", f"RX-DEMO-{i:02d}", f"MED-{i:02d}", pharmacist_users[i - 1], quantity=10 + i, status="DISPENSED", notes="Fictional sample dispensing record.")

for i in range(1, 11):
    add("homecare_request", f"HC-REQ-{i:02d}", f"demo_patient_{i:02d}", nurse_users[i - 1], date=f"today-{i}d", start_time="09:00", end_time="10:00", location=f"Demo Address {i:02d}, Dhaka", required_skills="Basic support (demo)", patient_notes="Synthetic request for software demonstration.", status="COMPLETED")
    add("homecare_review", f"HC-REVIEW-{i:02d}", f"HC-REQ-{i:02d}", rating=3 + (i % 3), comment="Fictional demo review. No real service was provided.")

for i in range(1, 11):
    add("bill", f"BILL-DEMO-{i:02d}", f"demo_patient_{i:02d}", f"APPT-PAST-{i:02d}", f"CONS-{i:02d}", description="Demo consultation and service charges", consultation_fee=1000 + i * 100, lab_fee=300 + i * 25, medicine_fee=200 + i * 20, other_fee=0, paid_amount=1500 + i * 100)
    add("payment", f"PAY-DEMO-{i:02d}", f"BILL-DEMO-{i:02d}", reception_users[i - 1], amount=1500 + i * 100, method=["CASH", "CARD", "MOBILE_BANKING", "BANK_TRANSFER"][i % 4], transaction_id=f"DEMO-PAY-{i:04d}", notes="Synthetic payment example; no real transaction.")

for i in range(1, 11):
    add("notification", f"NOTICE-{i:02d}", f"demo_patient_{i:02d}", notification_type=["APPOINTMENT", "HOME_CARE", "LAB", "PHARMACY", "BILLING"][i % 5], title=f"MediCore demo update {i:02d}", message="This is a fictional sample notification for the demo project.", link="", is_read=i % 2 == 0)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} rows to {OUTPUT}")
