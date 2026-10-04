from django.db.models import Q

from apps.accounts.models import User
from apps.hospitals.models import Hospital, Department
from apps.doctors.models import DoctorProfile
from apps.appointments.models import Appointment
from apps.medical_records.models import LabTest
from apps.pharmacy.models import Medicine


def global_search(query, user):
    query = query.strip()

    results = {
        "doctors": [],
        "patients": [],
        "hospitals": [],
        "departments": [],
        "medicines": [],
        "lab_tests": [],
        "appointments": [],
    }

    if not query:
        return results

    # Doctors
    results["doctors"] = (
        DoctorProfile.objects
        .select_related("user", "hospital", "department")
        .filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__public_id__icontains=query)
            | Q(specialization__icontains=query)
            | Q(qualification__icontains=query)
        )[:10]
    )

    # Patients
    if user.role in ["ADMIN", "DOCTOR", "NURSE", "RECEPTIONIST", "LAB", "PHARMACIST"]:
        results["patients"] = (
            User.objects
            .filter(
                role="PATIENT"
            )
            .filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
                | Q(public_id__icontains=query)
            )[:10]
        )

    # Hospitals
    results["hospitals"] = (
        Hospital.objects
        .filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(address__icontains=query)
        )[:10]
    )

    # Departments
    results["departments"] = (
        Department.objects
        .select_related("hospital")
        .filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
        )[:10]
    )

    # Medicines
    if user.role in ["ADMIN", "PHARMACIST", "DOCTOR"]:
        results["medicines"] = (
            Medicine.objects
            .filter(
                Q(name__icontains=query)
                | Q(generic_name__icontains=query)
                | Q(strength__icontains=query)
            )[:10]
        )

    # Lab Tests
    if user.role in ["ADMIN", "LAB", "DOCTOR", "RECEPTIONIST"]:
        results["lab_tests"] = (
            LabTest.objects
            .filter(
                Q(name__icontains=query)
                | Q(code__icontains=query)
            )[:10]
        )

    # Appointments
    if user.role in ["ADMIN", "DOCTOR", "RECEPTIONIST"]:
        results["appointments"] = (
            Appointment.objects
            .select_related("patient", "doctor", "department")
            .filter(
                Q(patient__public_id__icontains=query)
                | Q(doctor__user__public_id__icontains=query)
                | Q(doctor__user__first_name__icontains=query)
                | Q(doctor__user__last_name__icontains=query)
                | Q(department__name__icontains=query)
            )[:10]
        )

    return results