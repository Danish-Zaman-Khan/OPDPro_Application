from unittest import skipUnless
from datetime import date, timedelta

from django.conf import settings
from django.contrib.messages import constants
from django.contrib.messages.storage.cookie import CookieStorage
from django.db import connection
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from appointment.models import Appointment
from patients.models import Patient
from usermanagement.admin import ClinicUserCreationForm
from usermanagement.models import CustomUser
from user_notifications.models import Notification


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
        self.assertNotEqual(doctor.password, 'Safe-clinic-password-123!')

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

    @override_settings(OPD_LOCAL_DESKTOP=True)
    def test_desktop_login_page_shows_integrated_application_controls(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'desktop-app-bar')
        self.assertContains(response, 'Back up')
        self.assertContains(response, 'Restore')
        self.assertContains(response, 'desktop-app.js')

    @override_settings(OPD_LOCAL_DESKTOP=False)
    def test_web_login_page_does_not_show_desktop_application_controls(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'desktop-app-bar')

    def test_dashboard_renders_the_local_clinic_navigation(self):
        self.client.force_login(self.user)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saved on this computer')
        self.assertContains(response, 'Patients')
        self.assertNotContains(response, 'Admin tools')
        self.assertRegex(response.content.decode(), r'<style>\s*\.dashboard \{')

    def test_staff_without_admin_role_does_not_see_admin_actions(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.client.force_login(self.user)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Admin tools')
        self.assertNotContains(response, 'Clinic settings')

    def test_administrator_sees_admin_actions(self):
        administrator = CustomUser.objects.create_superuser(
            email='clinic-admin@example.test',
            password='Safe-clinic-password-123!',
            first_name='Clinic',
            last_name='Administrator',
            staff_role='admin',
        )
        self.client.force_login(administrator)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin tools')
        self.assertContains(response, 'Clinic settings')

    def test_dashboard_redirects_unauthenticated_users_to_login(self):
        response = self.client.get('/dashboard/')

        self.assertRedirects(response, '/?next=/dashboard/')

    def test_dashboard_query_count_does_not_grow_with_appointments(self):
        self.client.force_login(self.user)
        with CaptureQueriesContext(connection) as empty_queries:
            response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

        for index in range(3):
            patient = Patient.objects.create(
                first_name=f'Queue{index}',
                last_name='Patient',
                date_of_birth=date(1990, 1, 1),
                gender='M',
            )
            Appointment.objects.create(
                patient=patient,
                doctor=self.user,
                date=date.today() + timedelta(days=index),
                time=f'09:0{index}',
                status='Pending',
            )

        with CaptureQueriesContext(connection) as appointment_queries:
            response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(appointment_queries),
            len(empty_queries),
            'Dashboard queries should not increase once appointments are rendered.',
        )

    def test_staff_directory_shows_availability_without_chat_controls(self):
        inactive_staff = CustomUser.objects.create_user(
            email='inactive@example.test',
            password='Safe-clinic-password-123!',
            first_name='Inactive',
            last_name='Staff',
            staff_role='nurse',
            is_active=False,
        )
        self.client.force_login(self.user)

        response = self.client.get('/doctors/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active')
        self.assertContains(response, 'Inactive')
        self.assertContains(response, 'inactive@example.test')
        self.assertNotContains(response, 'Message')
        self.assertNotContains(response, 'bi-chat')
        self.assertNotContains(response, 'Admin tools')
        self.assertFalse(inactive_staff.is_active)

    def test_only_administrators_can_start_or_reply_to_messages(self):
        other_staff = CustomUser.objects.create_user(
            email='other-staff@example.test',
            password='Safe-clinic-password-123!',
            first_name='Other',
            last_name='Staff',
            staff_role='nurse',
        )
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.client.force_login(self.user)

        response = self.client.get(f'/notifications/send/to/{other_staff.pk}/')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Notification.objects.count(), 0)
        response = self.client.post(
            f'/notifications/send/to/{other_staff.pk}/',
            {'message': 'Unauthorized message.'},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Notification.objects.count(), 0)

        response = self.client.get(f'/doctors/{other_staff.pk}/edit/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get('/doctors/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'bi-chat')

        administrator = CustomUser.objects.create_superuser(
            email='clinic-admin@example.test',
            password='Safe-clinic-password-123!',
            first_name='Clinic',
            last_name='Administrator',
            staff_role='admin',
        )
        self.client.force_login(administrator)

        response = self.client.get(f'/notifications/send/to/{other_staff.pk}/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/doctors/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bi-chat')

        response = self.client.post(
            f'/notifications/send/to/{other_staff.pk}/',
            {'message': 'Please confirm your clinic schedule.'},
        )

        self.assertRedirects(response, '/notifications/')
        self.assertEqual(Notification.objects.get().user, other_staff)

        self.client.force_login(other_staff)
        inbox = self.client.get('/notifications/')
        self.assertContains(inbox, 'Please confirm your clinic schedule.')
        detail = self.client.get(f'/notifications/{Notification.objects.get().pk}/')
        self.assertEqual(detail.status_code, 200)
        self.assertNotContains(detail, 'Reply')

    @skipUnless(
        settings.OPD_LOCAL_DESKTOP or settings.DEBUG,
        'The authenticated local media route is enabled only in local mode.',
    )
    def test_local_media_requires_an_authenticated_session(self):
        response = self.client.get('/media/private-report.pdf')

        self.assertRedirects(
            response,
            '/?next=/media/private-report.pdf',
            fetch_redirect_response=False,
        )

        self.client.force_login(self.user)
        authenticated_response = self.client.get('/media/private-report.pdf')
        self.assertEqual(authenticated_response.status_code, 404)

    def test_invalid_login_does_not_leave_error_notifications_after_success(self):
        failed_login = self.client.post(
            '/',
            {'username': self.user.email, 'password': 'incorrect-password'},
        )
        self.assertTrue(failed_login.context['form'].non_field_errors())
        self.assertEqual(list(failed_login.context['messages']), [])

        old_request = RequestFactory().get('/')
        old_messages = CookieStorage(old_request)
        old_messages.add(constants.ERROR, 'Invalid credentials. Please try again.')
        old_response = HttpResponse()
        old_messages.update(old_response)
        self.client.cookies.update(old_response.cookies)

        response = self.client.post(
            '/',
            {'username': self.user.email, 'password': 'Safe-clinic-password-123!'},
        )

        self.assertRedirects(response, '/dashboard/')
        dashboard = self.client.get('/dashboard/')
        self.assertNotContains(dashboard, 'Invalid credentials')
        self.assertEqual(list(dashboard.context['messages']), [])

    def test_remember_me_keeps_session_for_fourteen_days(self):
        self.client.post(
            '/',
            {
                'username': self.user.email,
                'password': 'Safe-clinic-password-123!',
                'remember_me': 'on',
            },
        )

        expiry_age = self.client.session.get_expiry_age()
        self.assertLessEqual(expiry_age, 14 * 24 * 60 * 60)
        self.assertGreater(expiry_age, 14 * 24 * 60 * 60 - 10)

    def test_default_login_session_expires_when_browser_closes(self):
        self.client.post(
            '/',
            {'username': self.user.email, 'password': 'Safe-clinic-password-123!'},
        )

        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_non_staff_user_cannot_be_redirected_into_admin_tools(self):
        response = self.client.post(
            '/',
            {
                'username': self.user.email,
                'password': 'Safe-clinic-password-123!',
                'next': '/admin/',
            },
        )

        self.assertRedirects(response, '/dashboard/')

    def test_staff_user_can_return_to_admin_tools_after_sign_in(self):
        administrator = CustomUser.objects.create_superuser(
            email='clinic-admin@example.test',
            password='Safe-clinic-password-123!',
            first_name='Clinic',
            last_name='Administrator',
            staff_role='admin',
        )

        response = self.client.post(
            '/',
            {
                'username': administrator.email,
                'password': 'Safe-clinic-password-123!',
                'next': '/admin/',
            },
        )

        self.assertRedirects(response, '/admin/')

    def test_logout_requires_post_and_shows_signed_out_page(self):
        self.client.force_login(self.user)

        self.assertEqual(self.client.get('/logout/').status_code, 405)
        response = self.client.post('/logout/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are signed out')
        self.assertContains(response, 'Return to sign in')
        self.assertContains(response, 'Secure sign out')
        self.assertContains(response, 'Your clinic records remain saved on this computer.')

    def test_admin_tools_has_a_return_to_clinic_link(self):
        administrator = CustomUser.objects.create_superuser(
            email='clinic-admin@example.test',
            password='Safe-clinic-password-123!',
            first_name='Clinic',
            last_name='Administrator',
            staff_role='admin',
        )
        self.client.force_login(administrator)

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Return to OPDPro clinic')

        self.client.logout()
        login_page = self.client.get('/admin/login/')
        self.assertEqual(login_page.status_code, 200)
        self.assertContains(login_page, 'Return to OPDPro clinic')


class StaffApiPermissionTests(TestCase):
    def test_non_staff_user_cannot_manage_user_accounts_through_the_api(self):
        doctor = CustomUser.objects.create_user(
            email='doctor@example.test',
            password='Safe-clinic-password-123!',
            staff_role='doctor',
        )
        client = APIClient()
        client.force_authenticate(user=doctor)

        response = client.get('/api/usermanagement/users/')

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_manage_user_accounts_through_the_api(self):
        administrator = CustomUser.objects.create_superuser(
            email='clinic-admin@example.test',
            password='Safe-clinic-password-123!',
            staff_role='admin',
        )
        client = APIClient()
        client.force_authenticate(user=administrator)

        response = client.get('/api/usermanagement/users/')

        self.assertEqual(response.status_code, 200)
