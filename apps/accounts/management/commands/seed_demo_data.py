import csv
import json
import os
import re
from collections import Counter
from datetime import timedelta
from getpass import getpass
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.billing.models import Bill, Payment
from apps.doctors.models import DoctorProfile
from apps.hospitals.models import Department, Hospital
from apps.medical_records.models import Consultation, LabTest, LabTestOrder, Prescription, PrescriptionMedicine
from apps.notifications.models import Notification
from apps.nurses.models import HomeCareAvailability, HomeCareRequest, HomeCareReview, NurseProfile
from apps.patients.models import PatientProfile
from apps.pharmacy.models import DispensingRecord, Medicine
from apps.schedule_manager.models import Schedule


class Command(BaseCommand):
    help = "Import fictional MediCore demo records from data/medicore_demo_data.csv."

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / "data" / "medicore_demo_data.csv"
        if not csv_path.is_file():
            raise CommandError(f"Demo CSV not found: {csv_path}")

        password = os.environ.get("DEMO_PASSWORD") or getpass("Choose a password for all demo accounts (12+ characters): ")
        if len(password) < 12:
            raise CommandError("DEMO_PASSWORD must be at least 12 characters.")

        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        expected = {"feature", "key", "ref1", "ref2", "ref3", "payload_json"}
        if not rows or not expected.issubset(rows[0]):
            raise CommandError("CSV headers are missing or the CSV contains no records.")

        objects = {}
        counts = Counter()
        try:
            with transaction.atomic():
                for row in rows:
                    feature = row["feature"].strip()
                    key = row["key"].strip()
                    payload = json.loads(row["payload_json"] or "{}")
                    obj = self.import_row(feature, key, row, payload, objects, password)
                    objects.setdefault(feature, {})[key] = obj
                    counts[feature] += 1
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            raise CommandError(f"Could not import demo CSV: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Imported {sum(counts.values())} demo rows from {csv_path.name}."))
        self.stdout.write("Imported: " + ", ".join(f"{feature}={count}" for feature, count in sorted(counts.items())))
        self.stdout.write("All sample users share the password supplied through DEMO_PASSWORD.")

    @staticmethod
    def resolve_dates(value):
        if isinstance(value, dict):
            return {key: Command.resolve_dates(item) for key, item in value.items()}
        if isinstance(value, list):
            return [Command.resolve_dates(item) for item in value]
        if isinstance(value, str):
            match = re.fullmatch(r"today([+-])(\d+)d", value)
            if match:
                offset = int(match.group(2)) * (1 if match.group(1) == "+" else -1)
                return (timezone.localdate() + timedelta(days=offset)).isoformat()
        return value

    @staticmethod
    def ref(objects, feature, key):
        try:
            return objects[feature][key]
        except KeyError as exc:
            raise KeyError(f"Unknown {feature} reference {key!r}; check the CSV row order and keys.") from exc

    def import_row(self, feature, key, row, raw_data, objects, password):
        data = self.resolve_dates(raw_data)
        ref1, ref2, ref3 = row.get("ref1", ""), row.get("ref2", ""), row.get("ref3", "")
        User = get_user_model()

        if feature == "hospital":
            obj, _ = Hospital.objects.update_or_create(code=key, defaults=data)
        elif feature == "department":
            hospital = self.ref(objects, "hospital", ref1)
            obj, _ = Department.objects.update_or_create(code=key, defaults={**data, "hospital": hospital})
        elif feature == "user":
            obj, created = User.objects.get_or_create(username=key)
            for field, value in data.items():
                setattr(obj, field, value)
            if created:
                obj.set_password(password)
            obj.save()
        elif feature == "patient_profile":
            user = self.ref(objects, "user", key)
            obj, _ = PatientProfile.objects.update_or_create(user=user, defaults=data)
        elif feature == "doctor_profile":
            user = self.ref(objects, "user", key)
            obj, _ = DoctorProfile.objects.update_or_create(
                user=user,
                defaults={**data, "hospital": self.ref(objects, "hospital", ref1), "department": self.ref(objects, "department", ref2)},
            )
        elif feature == "nurse_profile":
            user = self.ref(objects, "user", key)
            obj, _ = NurseProfile.objects.update_or_create(user=user, defaults={**data, "hospital": self.ref(objects, "hospital", ref1)})
        elif feature == "homecare_availability":
            nurse = self.ref(objects, "nurse_profile", ref1)
            obj, _ = HomeCareAvailability.objects.update_or_create(nurse=nurse, day=data["day"], start_time=data["start_time"], defaults={k: v for k, v in data.items() if k not in {"day", "start_time"}})
        elif feature == "schedule":
            user = self.ref(objects, "user", ref1)
            hospital = self.ref(objects, "hospital", ref2) if ref2 else None
            department = self.ref(objects, "department", ref3) if ref3 else None
            lookup = {"user": user, "date": data["date"], "start_time": data["start_time"], "end_time": data["end_time"], "schedule_type": data["schedule_type"]}
            obj, _ = Schedule.objects.update_or_create(**lookup, defaults={**data, "hospital": hospital, "department": department})
        elif feature == "appointment":
            patient = self.ref(objects, "user", ref1)
            doctor = self.ref(objects, "doctor_profile", ref2)
            department = self.ref(objects, "department", ref3)
            lookup = {"doctor": doctor, "date": data["date"], "start_time": data["start_time"], "end_time": data["end_time"]}
            obj, _ = Appointment.objects.update_or_create(**lookup, defaults={**data, "patient": patient, "department": department})
        elif feature == "consultation":
            appointment = self.ref(objects, "appointment", ref1)
            obj, _ = Consultation.objects.update_or_create(appointment=appointment, defaults={**data, "patient": appointment.patient, "doctor": appointment.doctor.user})
        elif feature == "prescription":
            consultation = self.ref(objects, "consultation", ref1)
            obj, _ = Prescription.objects.update_or_create(consultation=consultation, defaults={**data, "patient": consultation.patient, "doctor": consultation.doctor})
        elif feature == "prescription_medicine":
            prescription = self.ref(objects, "prescription", ref1)
            obj, _ = PrescriptionMedicine.objects.get_or_create(prescription=prescription, medicine_name=data["medicine_name"], dosage=data["dosage"], frequency=data["frequency"], duration=data["duration"], defaults={"instructions": data.get("instructions", "")})
        elif feature == "lab_test":
            obj, _ = LabTest.objects.update_or_create(code=data["code"], defaults={k: v for k, v in data.items() if k != "code"})
        elif feature == "lab_order":
            consultation = self.ref(objects, "consultation", ref1)
            test = self.ref(objects, "lab_test", ref2)
            obj, _ = LabTestOrder.objects.update_or_create(order_id=key, defaults={**data, "consultation": consultation, "patient": consultation.patient, "doctor": consultation.doctor, "test": test})
        elif feature == "medicine":
            obj, _ = Medicine.objects.update_or_create(name=data["name"], strength=data["strength"], defaults={k: v for k, v in data.items() if k not in {"name", "strength"}})
        elif feature == "dispensing":
            prescription = self.ref(objects, "prescription", ref1)
            medicine = self.ref(objects, "medicine", ref2)
            pharmacist = self.ref(objects, "user", ref3)
            obj, _ = DispensingRecord.objects.get_or_create(prescription=prescription, medicine=medicine, pharmacist=pharmacist, quantity=data["quantity"], defaults={k: v for k, v in data.items() if k != "quantity"})
        elif feature == "homecare_request":
            patient = self.ref(objects, "user", ref1)
            nurse = self.ref(objects, "nurse_profile", ref2)
            lookup = {"patient": patient, "nurse": nurse, "date": data["date"], "start_time": data["start_time"], "end_time": data["end_time"]}
            obj, _ = HomeCareRequest.objects.update_or_create(**lookup, defaults={**data, "patient": patient, "nurse": nurse})
        elif feature == "homecare_review":
            request = self.ref(objects, "homecare_request", ref1)
            obj, _ = HomeCareReview.objects.update_or_create(request=request, defaults={**data, "patient": request.patient, "nurse": request.nurse})
        elif feature == "bill":
            patient = self.ref(objects, "user", ref1)
            appointment = self.ref(objects, "appointment", ref2)
            consultation = self.ref(objects, "consultation", ref3)
            obj, _ = Bill.objects.update_or_create(bill_id=key, defaults={**data, "patient": patient, "appointment": appointment, "consultation": consultation})
        elif feature == "payment":
            bill = self.ref(objects, "bill", ref1)
            paid_by = self.ref(objects, "user", ref2)
            obj, _ = Payment.objects.get_or_create(transaction_id=data["transaction_id"], defaults={**data, "bill": bill, "paid_by": paid_by})
        elif feature == "notification":
            recipient = self.ref(objects, "user", ref1)
            obj, _ = Notification.objects.update_or_create(recipient=recipient, title=data["title"], defaults=data)
        else:
            raise ValueError(f"Unsupported feature {feature!r} on record {key!r}.")
        return obj
