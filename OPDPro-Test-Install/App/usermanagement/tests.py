from django.test import TestCase

from usermanagement.admin import ClinicUserCreationForm
from usermanagement.models import CustomUser


class ClinicStaffCreationTests(TestCase):
    def test_administrator_can_create_a_doctor_account(self):
        form = ClinicUserCreationForm(
            data={
                'email': 'doctor@example.test',
                'first_name': 'Anita',
                'last_name': 'Rao',
                'mobile_number': '9876543210',
                'staff_role': 'doctor',
                'specialization': 'Dentistry',
                'license_number': 'STATE-REG-123',
                'password1': 'Safe-clinic-password-123!',
                'password2': 'Safe-clinic-password-123!',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        doctor = form.save()

        self.assertEqual(doctor.email, 'doctor@example.test')
        self.assertEqual(doctor.staff_role, 'doctor')
        self.assertEqual(doctor.specialization, 'Dentistry')
        self.assertTrue(doctor.check_password('Safe-clinic-password-123!'))

    def test_first_run_administrator_is_a_superuser(self):
        administrator = CustomUser.objects.create_superuser(
            email='clinic-admin@example.test',
            password='Safe-clinic-password-123!',
            first_name='Clinic',
            last_name='Administrator',
            staff_role='admin',
        )

        self.assertTrue(administrator.is_superuser)
        self.assertTrue(administrator.is_staff)
        self.assertTrue(administrator.check_password('Safe-clinic-password-123!'))


class ClinicPageRenderTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='clinic-user@example.test',
            password='Safe-clinic-password-123!',
            first_name='Clinic',
            last_name='User',
            staff_role='doctor',
        )

    def test_login_page_renders_without_public_registration(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Need an account? Ask your clinic administrator.')
        self.assertNotContains(response, 'Create account')

    def test_dashboard_renders_the_local_clinic_navigation(self):
        self.client.force_login(self.user)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saved on this computer')
        self.assertContains(response, 'Patients')
        self.assertRegex(response.content.decode(), r'<style>\s*\.dashboard \{')

    def test_dashboard_redirects_unauthenticated_users_to_login(self):
        response = self.client.get('/dashboard/')

        self.assertRedirects(response, '/?next=/dashboard/')
