from django.test import TestCase

from doctors.forms import DoctorEditForm
from usermanagement.forms import UserUpdateProfileForm
from usermanagement.models import CustomUser


class DoctorSpecializationProfileTests(TestCase):
    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            email='dentist@example.test',
            password='Test-password-123!',
            first_name='Asha',
            last_name='Shah',
            staff_role='doctor',
        )

    def test_account_profile_can_save_specialization_and_registration_number(self):
        form = UserUpdateProfileForm(
            instance=self.doctor,
            data={
                'first_name': 'Asha',
                'last_name': 'Shah',
                'email': 'dentist@example.test',
                'mobile_number': '9876543210',
                'specialization': 'Dentistry',
                'license_number': 'STATE-REG-123',
            },
        )

        self.assertTrue(form.is_valid(), form.errors)
        doctor = form.save()

        self.assertEqual(doctor.specialization, 'Dentistry')
        self.assertEqual(doctor.license_number, 'STATE-REG-123')

    def test_doctor_profile_edit_can_save_specialization(self):
        form = DoctorEditForm(
            instance=self.doctor,
            data={
                'first_name': 'Asha',
                'last_name': 'Shah',
                'email': 'dentist@example.test',
                'mobile_number': '9876543210',
                'specialization': 'Oral Surgery',
                'license_number': 'STATE-REG-456',
            },
        )

        self.assertTrue(form.is_valid(), form.errors)
        doctor = form.save()

        self.assertEqual(doctor.specialization, 'Oral Surgery')
        self.assertEqual(doctor.license_number, 'STATE-REG-456')
