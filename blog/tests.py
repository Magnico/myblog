from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from django.db.utils import IntegrityError
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
            Post.objects.create(title=None, body=None,author=testuser).full_clean()
            Post.objects.create(title="test1", body=None,author=testuser).full_clean()
            Post.objects.create(title=None, body="test2",author=testuser).full_clean()
            Post.objects.create(title=None, body="test2",author=None).full_clean()

    def test_post_empty_fields(self):
        testuser = User.objects.create_user(username="testing", password="testpassword")
        with self.assertRaises(ValidationError):
            Post.objects.create(title="", body="",author=testuser).full_clean()
            Post.objects.create(title="test1", body="",author=testuser).full_clean()
            Post.objects.create(title="", body="test2",author=testuser).full_clean()

    def test_post_user_delete(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        Post.objects.create(title="test1", body="test1", author=user)
        Post.objects.create(title="test2", body="test2", author=user)
        Post.objects.create(title="test3", body="test3", author=user)
        user.delete()
        self.assertEqual(Post.objects.count(), 0)