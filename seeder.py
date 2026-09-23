import os
import sys
import django
import json

# ১. জ্যাঙ্গো কনফিগারেশন সেটআপ
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# ২. জ্যাঙ্গো মডেলসমূহ ইম্পোর্ট
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from apps.hospitals.models import Hospital, Department
from apps.doctors.models import DoctorProfile
from apps.nurses.models import NurseProfile

User = get_user_model()

def seed_data():
    print("Reading JSON data from hospital_data.json...")
    try:
        with open('hospital_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: hospital_data.json file not found in root directory!")
        return

    default_password = "password123"

    # ৩. ডিফল্ট হসপিটাল গেট বা ক্রিয়েট
    print("Processing Hospital...")
    default_hospital, _ = Hospital.objects.get_or_create(
        name="MediCore General Hospital",
        defaults={
            "address": "Dhaka, Bangladesh",
            "phone": "+880123456789"
        }
    )

    # ৪. ডিপার্টমেন্ট গেট বা ক্রিয়েট
    print("Processing Departments...")
    departments_pool = {}
    unique_depts = set()
    for doc in data.get('doctors', []):
        unique_depts.add(doc['department'])
    for nurse in data.get('nurses', []):
        unique_depts.add(nurse['department'])

    for dept_name in unique_depts:
        dept, _ = Department.objects.get_or_create(
            name=dept_name,
            hospital=default_hospital
        )
        departments_pool[dept_name] = dept

    # ৫. ডক্টর এবং তাদের প্রোফাইল তৈরি (KeyError ফিক্সড)
    print("Creating Doctors and Profiles...")
    for doc in data.get('doctors', []):
        if not User.objects.filter(username=doc['username']).exists():
            # ফাইলের 'name' ফিল্ড থেকে First Name এবং Last Name আলাদা করা হচ্ছে
            full_name = doc.get('name', 'Doctor User').split(' ')
            f_name = full_name[0]
            l_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''

            user = User.objects.create_user(
                username=doc['username'],
                email=doc['email'],
                first_name=f_name,
                last_name=l_name,
                password=default_password,
                role=Role.DOCTOR,
                is_verified=True
            )
            DoctorProfile.objects.create(
                user=user,
                hospital=default_hospital,
                department=departments_pool.get(doc['department']),
                specialization=doc.get('specialization', 'General Practice'),
                qualification="MBBS, MD",
                experience_years=doc.get('experience_years', 5),
                phone=doc.get('phone', '+8801700000000'),
                consultation_fee=doc.get('consultation_fee', 500),
                bio=f"Experienced doctor specializing in {doc.get('specialization', 'Healthcare')}."
            )

    # ৬. নার্স এবং তাদের প্রোফাইল তৈরি (KeyError ফিক্সড)
    print("Creating Nurses and Profiles...")
    for nurse in data.get('nurses', []):
        if not User.objects.filter(username=nurse['username']).exists():
            # ফাইলের 'name' ফিল্ড থেকে First Name এবং Last Name আলাদা করা হচ্ছে
            full_name = nurse.get('name', 'Nurse User').split(' ')
            f_name = full_name[0]
            l_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''

            user = User.objects.create_user(
                username=nurse['username'],
                email=nurse['email'],
                first_name=f_name,
                last_name=l_name,
                password=default_password,
                role=Role.NURSE,
                is_verified=True
            )
            NurseProfile.objects.create(
                user=user,
                hospital=default_hospital,
                department=departments_pool.get(nurse['department']),
                qualification="BSc in Nursing",
                experience_years=nurse.get('experience_years', 3),
                phone=nurse.get('phone', '+8801800000000'),
                skills="Patient Care, ICU Support, Emergency Response",
                hourly_rate=nurse.get('hourly_rate', 200),
                is_available_for_homecare=nurse.get('is_available_for_homecare', True),
                bio="Dedicated professional nurse."
            )

    # ੭. ল্যাব অ্যাসিস্ট্যান্ট তৈরি (KeyError ফিক্সড)
    print("Creating Lab Assistants...")
    for lab in data.get('labs', []):
        if not User.objects.filter(username=lab['username']).exists():
            full_name = lab.get('name', 'Lab Staff').split(' ')
            f_name = full_name[0]
            l_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''

            User.objects.create_user(
                username=lab['username'],
                email=lab['email'],
                first_name=f_name,
                last_name=l_name,
                password=default_password,
                role=Role.LAB,
                is_verified=True
            )

    # ৮. পেশেন্ট তৈরি (KeyError ফিক্সড)
    print("Creating Patients...")
    for patient in data.get('patients', []):
        if not User.objects.filter(username=patient['username']).exists():
            full_name = patient.get('name', 'Patient User').split(' ')
            f_name = full_name[0]
            l_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''

            User.objects.create_user(
                username=patient['username'],
                email=patient['email'],
                first_name=f_name,
                last_name=l_name,
                password=default_password,
                role=Role.PATIENT,
                is_verified=True
            )

    print("Successfully seeded all data!")

if __name__ == '__main__':
    seed_data()
