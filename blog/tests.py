from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.utils import DataError
from django.db.utils import IntegrityError
from django.db import transaction
from .models import Post
import pytest

# Create your tests here.
@pytest.mark.django_db
class PostTestCase(TestCase):

    def test_post_character_limit(self):
        testuser = User.objects.create_user(username="testing", password="testpassword")
        content = "x"*256
        title = "x"*101
        with self.assertRaises(DataError) as e:
            Post.objects.create(title=title, body=content, author=testuser).full_clean()

    def test_post_null_fields(self):
        testuser = User.objects.create_user(username="testing", password="testpassword")
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title=None, body=None,author=None).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title=None, body=None,author=testuser).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title="test1", body=None,author=testuser).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title=None, body="test2",author=testuser).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title="test3", body="test3",author=None).full_clean()

    def test_post_empty_fields(self):
        testuser = User.objects.create_user(username="testing", password="testpassword")

        with self.assertRaises(ValidationError):
            Post.objects.create(title="", body="",author=testuser).full_clean()
        
        with self.assertRaises(ValidationError):
            Post.objects.create(title="test1", body="",author=testuser).full_clean()
        
        with self.assertRaises(ValidationError):
            Post.objects.create(title="", body="test2",author=testuser).full_clean()

    def test_post_user_delete(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        Post.objects.create(title="test1", body="test1", author=user)
        Post.objects.create(title="test2", body="test2", author=user)
        Post.objects.create(title="test3", body="test3", author=user)
        user.delete()
        self.assertEqual(Post.objects.count(), 0)

@pytest.mark.django_db
class UserLogSignTest(TestCase):
    def setUp(self):
        User.objects.create_user(username="testuser2", password="testpassword2")

    def test_user_signup(self):
        response = self.client.get(reverse('blog:signup'))

        #Check if page loads
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('blog:signup'),{
            'username':'testuser',
            'email':'testing@this.user',
            'password1':'thisisatestpasswordforuser',
            'password2':'thisisatestpasswordforuser'}
            )
        
        #Check if redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blog:login'))

        #Check if user was created
        user = get_object_or_404(User, username='testuser')
        self.assertEqual(user.email, 'testing@this.user')

    def test_user_login_logout(self):
        response = self.client.get(reverse('blog:login'))
        
        #Check login page loads
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('blog:login'),{
            'username': 'testuser2',
            'password': 'testpassword2'
        })

        #Check if redirect to index page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blog:index'))

        #Check if user is logged in
        self.assertIsNotNone(self.client.session.get('_auth_user_id'))

        response = self.client.get(reverse('blog:logout'))
        
        #Check if redirect to index page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blog:login'))

        #Check if user is logged out
        self.assertIsNone(self.client.session.get('_auth_user_id'))
