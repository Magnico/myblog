from django.db.utils import DataError, IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Post, Comment
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
import pytest

# Create your tests here.
@pytest.mark.django_db
class PostTestCase(TestCase):

    def test_post_character_limit(self):
        testuser = User.objects.create_user(username="testing", password="testpassword")
        content = "x"*256
        title = "x"*101
        with self.assertRaises(DataError) as e:
            with transaction.atomic():
                Post.objects.create(title=title, body='content', author=testuser).full_clean()
        with self.assertRaises(DataError) as e:
            with transaction.atomic():
                Post.objects.create(title='title', body=content, author=testuser).full_clean()

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
class CommentTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(username="testuser", password="testpassword")
        self.user = User.objects.get(username="testuser")
        Post.objects.create(title="test1", body="test1", author=self.user)
        self.post = Post.objects.get(title="test1")

    def test_comment_character_limit(self):
        content = "x"*256
        print(len(content))
        with self.assertRaises(DataError):
            Comment.objects.create(body=content, author=self.user, post=self.post).full_clean()
    
    def test_comment_null_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(body=None, author=self.user, post=self.post).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(body="test", author=self.user, post=None).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(body=None, author=self.user, post=None).full_clean()    

    def test_comment_empty_fields(self):
        with self.assertRaises(ValidationError):
            Comment.objects.create(body="", author=self.user, post=self.post).full_clean()
    
    def test_comment_user_delete(self):
        user = User.objects.create_user(username="testuser2", password="testpassword")
        Comment.objects.create(body="test1", author=user, post=self.post)
        Comment.objects.create(body="test2", author=user, post=self.post)
        Comment.objects.create(body="test3", author=user, post=self.post)
        user.delete()
        for comment in Comment.objects.all():
            self.assertEqual(comment.author, None)
         
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

@pytest.mark.django_db
class PostAPITest(APITestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="testpassword")
        Post.objects.create(title="test", body="test", author=User.objects.get(username="testuser"))
        self.user = User.objects.get(username="testuser")

    def test_post_list(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)
        #Getting the response from the API
        response = self.client.get(reverse('blog:post-list'))

        #Checking if the response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = Post.objects.count()
        self.assertEqual(count, response.data['count'])

        #Creating new posts
        Post.objects.create(title="test1", body="test1", author=self.user)
        Post.objects.create(title="test2", body="test2", author=self.user)
        Post.objects.create(title="test3", body="test3", author=self.user)

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-list'))
        
        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = Post.objects.count()
        self.assertEqual(count, response.data['count'])

    def test_post_create(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the response from the API
        response = self.client.post(reverse('blog:post-list'),{
            'title': 'testing',
            'body': 'testing'
        })

        #Checking if response is OK
        self.assertEqual(response.status_code, 201)

        #Checking if the response is the same as the database
        post = get_object_or_404(Post, title="testing")
        self.assertEqual(post.title, response.data['title'])
        self.assertEqual(post.body, response.data['body'])
        self.assertEqual(post.author.username, response.data['author'])
    
    def test_post_retrieve(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the pk of the post
        post = Post.objects.get();

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-detail', kwargs={'pk':post.pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        self.assertEqual(post.title, response.data['title'])
        self.assertEqual(post.body, response.data['body'])
        self.assertEqual(post.author.username, response.data['author'])
    
    def test_post_patch(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the pk of the post
        post = Post.objects.get();

        #Getting the response from the API
        response = self.client.patch(reverse('blog:post-detail', kwargs={'pk':post.pk}),{
            'title': 'testing',
            'body': 'testing'
        })

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the databaset
        post = Post.objects.get(pk=post.pk);
        self.assertEqual(post.title, response.data['title'])
        self.assertEqual(post.body, response.data['body'])
        self.assertEqual(post.author.username, response.data['author'])
    
    def test_post_delete(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the pk of the post
        post = Post.objects.get();

        #Getting the response from the API
        response = self.client.delete(reverse('blog:post-detail', kwargs={'pk':post.pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 204)

        #Checking if the response is the same as the database
        count = Post.objects.count()
        self.assertEqual(count, 0)

@pytest.mark.django_db
class CommentAPITest(APITestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="testpassword")
        self.user = User.objects.get(username="testuser")
        Post.objects.create(title="test", body="test", author=self.user)
        self.post = Post.objects.get(title="test")
        Comment.objects.create(body="test", post=self.post, author=self.user)
        self.comment = Comment.objects.get(body="test")

    def test_comment_list(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)
        #Getting the response from the API
        response = self.client.get(reverse('blog:comment-list'), kwargs={'post_pk':self.post.pk})

        #Checking if the response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = Comment.objects.count()
        self.assertEqual(count, response.data['count'])

        #Creating new comments
        Comment.objects.create(body="test1", post=self.post, author=self.user)
        Comment.objects.create(body="test2", post=self.post, author=self.user)
        Comment.objects.create(body="test3", post=self.post, author=self.user)

        #Getting the response from the API
        response = self.client.get(reverse('blog:comment-list'), kwargs={'post_pk':self.post.pk})
        
        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = Comment.objects.count()
        self.assertEqual(count, response.data['count'])

    def test_comment_create(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the response from the API
        response = self.client.post(reverse('blog:comment-list'),{
            'body': 'testing',
            'post': self.post.pk
        })

        #Checking if response is OK
        self.assertEqual(response.status_code, 201)

        #Checking if the response is the same as the database
        comment = get_object_or_404(Comment, body="testing")
        self.assertEqual(comment.body, response.data['body'])
        self.assertEqual(comment.author.username, response.data['author'])
    
    def test_comment_retrieve(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)


        #Getting the response from the API
        response = self.client.get(reverse('blog:comment-detail', kwargs={'pk':self.comment.pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        self.assertEqual(self.comment.body, response.data['body'])
        self.assertEqual(self.comment.author.username, response.data['author'])

    def test_comment_patch(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the response from the API
        response = self.client.patch(reverse('blog:comment-detail', kwargs={'pk':self.comment.pk}),{
            'body': 'testing changes'
        })

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the databaset
        comment = Comment.objects.get(pk=self.comment.pk);
        self.assertEqual(comment.body, response.data['body'])
        self.assertEqual(comment.author.username, response.data['author'])

    def test_comment_delete(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the response from the API
        response = self.client.delete(reverse('blog:comment-detail', kwargs={'pk':self.comment.pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 204)

        #Checking if the post is deleted
        count = Comment.objects.count()
        self.assertEqual(count, 0)