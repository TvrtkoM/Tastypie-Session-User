import json

from django.test import TestCase
from django.contrib.auth.models import User

from tastypie.test import ResourceTestCase

from registration.models import RegistrationProfile

from .forms import LoginForm


class LoginFormTest(TestCase):
    def setUp(self):
        self.errors = LoginForm.error_messages
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def test_valid_form(self):
        form = LoginForm({
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(form.is_valid(), True)

    def test_invalid_login_form(self):
        form = LoginForm({
            'username': 'fail',
            'password': 'user'
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.non_field_errors(), [unicode(self.errors['invalid_login'])])

    def test_empty_login_form1(self):
        form = LoginForm({
            'username': '',
            'password': 'user'
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.non_field_errors(), [unicode(self.errors['empty'])])

    def test_empty_login_form2(self):
        form = LoginForm({
            'username': '',
            'password': ''
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.non_field_errors(), [unicode(self.errors['empty'])])

    def test_inactive_login_form(self):
        self.user.is_active = False
        self.user.save()
        form = LoginForm({
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.non_field_errors(), [unicode(self.errors['inactive'])])


class CreateUserResourceTest(ResourceTestCase):
    def setUp(self):
        super(CreateUserResourceTest, self).setUp()

        self.username = 'testuser'
        self.password = 'testpassword'
        self.email = 'testemail@example.com'

        self.post_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testemail@email.com'
        }
        self.post_data2 = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testemail2@email.com'
        }
        self.post_data3 = {
            'username': 'testuser2',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testemail@email.com'
        }

    def test_register(self):
        resp1 = self.api_client.post(
            '/api/v1/new-user/',
            data=self.post_data
        )
        user = User.objects.get(username=self.username)
        self.assertHttpCreated(resp1)
        self.assertEqual(user.is_active, False)

        # try again - should response with HttpBadRequest
        resp2 = self.api_client.post(
            '/api/v1/new-user/',
            data=self.post_data
        )
        self.assertHttpBadRequest(resp2)
        self.assertEqual(
            json.loads(resp2.content),
            {
                'errors': {
                    'username': [u'User with this username already exists.'],
                    'email': [u'User with this e-mail already exists.']
                },
                'reason': [u'Please enter correct data in the form. All fields are required.'],
                'success': False
            },
            )

        # try again with same username but different email - should respond with HttpBadRequest again
        resp3 = self.api_client.post(
            '/api/v1/new-user/',
            data=self.post_data2
        )
        self.assertHttpBadRequest(resp3)
        self.assertEqual(
            json.loads(resp3.content),
            {
                'errors': {
                    'username': [u'User with this username already exists.'],
                    },
                'reason': [u'Please enter correct data in the form. All fields are required.'],
                'success': False
            }
        )

        # try again with same email but different username - should respond with HttpBadRequest again
        resp4 = self.api_client.post(
            '/api/v1/new-user/',
            data=self.post_data3
        )
        self.assertHttpBadRequest(resp3)
        self.assertEqual(
            json.loads(resp4.content),
            {
                'errors': {
                    'email': [u'User with this e-mail already exists.']
                },
                'reason': [u'Please enter correct data in the form. All fields are required.'],
                'success': False
            }
        )

    def test_invalid(self):
        resp1 = self.api_client.post(
            '/api/v1/new-user/',
            data={
                'username': '',
                'password1': '',
                'password2': '',
                'email': '',
                }
        )
        self.assertHttpBadRequest(resp1)
        self.assertEqual(
            json.loads(resp1.content),
            {
                'reason': [u'Please enter correct data in the form. All fields are required.'],
                'errors': {
                    'username': [u'This field is required.'],
                    'email': [u'This field is required.'],
                    'password1': [u'This field is required.'],
                    },
                'success': False
            }
        )
        resp2 = self.api_client.post(
            '/api/v1/new-user/',
            data={
                'username': 'fail_username',
                'password1': '',
                'password2': '',
                'email': '',
                }
        )
        self.assertHttpBadRequest(resp2)
        self.assertEqual(
            json.loads(resp2.content),
            {
                'reason': [u'Please enter correct data in the form. All fields are required.'],
                'errors': {
                    'email': [u'This field is required.'],
                    'password1': [u'This field is required.'],
                    },
                'success': False
            }
        )
        resp3 = self.api_client.post(
            '/api/v1/new-user/',
            data={
                'username': 'fail_username',
                'password1': '',
                'password2': 'f4il_passsss',
                'email': 'fail@email.com',
                }
        )
        self.assertHttpBadRequest(resp3)
        self.assertEqual(
            json.loads(resp3.content),
            {
                'reason': [u'Please enter correct data in the form. All fields are required.'],
                'errors': {
                    'password1': [u'This field is required.'],
                    },
                'success': False
            }
        )

    def test_password_error(self):
        resp1 = self.api_client.post(
            '/api/v1/new-user/',
            data={
                'username': 'failusername',
                'password1': 'f4il_pass',
                'password2': 'fail2_pass',
                'email': 'fail@email.com',
                }
        )
        self.assertHttpBadRequest(resp1)
        self.assertEqual(
            json.loads(resp1.content),
            {
                'reason': [u'Entered passwords do not match.'],
                'errors': {
                    'password2': [u'Please retype the correct password.'],
                    },
                'success': False
            }
        )


class UserResourceTest(ResourceTestCase):
    def setUp(self):
        super(UserResourceTest, self).setUp()
        self.user = RegistrationProfile.objects.create_inactive_user(
            'test_user',
            'test_email@example.com',
            'test_password',
            None,
            False
        )
        self.errors = LoginForm.error_messages
        self.rp = RegistrationProfile.objects.get(user=self.user)

    def test_valid_activation(self):
        resp = self.api_client.get(
            '/api/v1/user/activate/',
            data={'key': self.rp.activation_key}
        )
        self.assertHttpOK(resp)

    def test_invalid_activation(self):
        resp = self.api_client.get(
            '/api/v1/user/activate/',
            data={'key': 'invalid_key'}
        )
        self.assertHttpBadRequest(resp)

    def test_login_activated(self):
        self.api_client.get(
            '/api/v1/user/activate/',
            data={'key': self.rp.activation_key}
        )
        resp = self.client.post(
            '/api/v1/user/login/',
            data={
                'username': 'test_user',
                'password': 'test_password'
            }
        )
        self.assertHttpOK(resp)

    def test_login_inactive(self):
        resp = self.client.post(
            '/api/v1/user/login/',
            data={
                'username': 'test_user',
                'password': 'test_password'
            }
        )
        self.assertHttpNotFound(resp)
        self.assertEqual(
            resp.content,
            json.dumps({'reason': [unicode(self.errors['inactive'])], 'success': False})
        )

    def test_invalid_login1(self):
        resp = self.client.post(
            '/api/v1/user/login/',
            data={
                'username': 'fail',
                'password': 'login'
            }
        )
        self.assertHttpNotFound(resp)
        self.assertEqual(
            resp.content,
            json.dumps({'reason': [unicode(self.errors['invalid_login'])], 'success': False})
        )

    def test_invalid_login2(self):
        resp = self.client.post(
            '/api/v1/user/login/',
            data={
                'username': '',
                'password': ''
            }
        )
        self.assertHttpNotFound(resp)
        self.assertEqual(
            resp.content,
            json.dumps({'reason': [unicode(self.errors['empty'])], 'success': False})
        )
