from apps.appointments.models import Appointment


def doctor_has_patient_relationship(doctor, patient):
    return Appointment.objects.filter(
        doctor__user=doctor,
        patient=patient,
    ).exists()