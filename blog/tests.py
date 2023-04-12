from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import DataError, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Post, Comment, UserTag
from django.db import transaction
from dateutil.parser import parse
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
import tempfile
import pytest
import shutil
import os

# Create your tests here.
@pytest.mark.django_db
class PostTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(username="testuser", password="testpassword")
        self.user = User.objects.get(username="testuser")
        self.media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.media_root

    def tearDown(self):
        shutil.rmtree(self.media_root)

    def test_post_character_limit(self):
        content = "x"*256
        title = "x"*101
        with self.assertRaises(DataError) as e:
            with transaction.atomic():
                Post.objects.create(title=title, body='content', author=self.user).full_clean()
        with self.assertRaises(DataError) as e:
            with transaction.atomic():
                Post.objects.create(title='title', body=content, author=self.user).full_clean()

    def test_post_null_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title=None, body=None,author=None).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title=None, body=None,author=self.user).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title="test1", body=None,author=self.user).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title=None, body="test2",author=self.user).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(title="test3", body="test3",author=None).full_clean()

    def test_post_empty_fields(self):
        with self.assertRaises(ValidationError):
            Post.objects.create(title="", body="",author=self.user).full_clean()

        with self.assertRaises(ValidationError):
            Post.objects.create(title="test1", body="",author=self.user).full_clean()
        
        with self.assertRaises(ValidationError):
            Post.objects.create(title="", body="test2",author=self.user).full_clean()

    def test_post_user_delete(self):
        Post.objects.create(title="test1", body="test1", author=self.user)
        Post.objects.create(title="test2", body="test2", author=self.user)
        Post.objects.create(title="test3", body="test3", author=self.user)
        self.user.delete()
        self.assertEqual(Post.objects.count(), 0)
    
    def test_post_img_saved(self):
        #create an image file
        img_file = SimpleUploadedFile("test_img_save.jpg", b"file_content", content_type="image/jpeg")

        #Create a post with the image
        Post.objects.create(title="test1", body="test1", author=self.user, img=img_file)
        post = Post.objects.get(title="test1")

        #check if the image have the correct path
        expected_path = f'uploads/images/{post.created_at.strftime("%Y/%m/%d")}/test_img_save.jpg'
        self.assertEqual(post.img.name, expected_path)

        #check if the image exists
        self.assertTrue(os.path.exists(post.img.path))

    def test_post_img_delete(self):
        #create an image file
        img_file = SimpleUploadedFile("test_delete.jpg", b"file_content", content_type="image/jpeg")

        #Create a post with the image
        Post.objects.create(title="test1", body="test1", author=self.user, img=img_file)
        post = Post.objects.get(title="test1")

        #check if the image exists
        self.assertTrue(os.path.exists(post.img.path))

        path = post.img.path

        #delete the post
        post.delete()

        #check if the image was deleted
        self.assertFalse(os.path.exists(path))

    def test_post_img_update(self):
        #create an image file
        img_file = SimpleUploadedFile("test_update_1.jpg", b"file_content", content_type="image/jpeg")

        #Create a post with the image
        Post.objects.create(title="test1", body="test1", author=self.user, img=img_file)
        post = Post.objects.get(title="test1")

        #check if the image exists
        self.assertTrue(os.path.exists(post.img.path))

        #create a new image file
        img_file2 = SimpleUploadedFile("test_update_2.jpg", b"file_content", content_type="image/jpeg")

        #update the post with the new image
        post.img = img_file2
        post.save()

        #check if the image have the correct path
        expected_path = f'uploads/images/{post.created_at.strftime("%Y/%m/%d")}/test_update_2.jpg'
        self.assertEqual(post.img.name, expected_path)

        #check if the image exists
        self.assertTrue(os.path.exists(post.img.path))

        #check if the old image was deleted
        self.assertFalse(os.path.exists(post.img.path.replace("test_update_2.jpg", "test_update_1.jpg")))

    def test_post_comments_count(self):
        Post.objects.create(title="test1", body="test1", author=self.user)
        post = Post.objects.get(title="test1")
        Comment.objects.create(body="test1", author=self.user, post=post)
        Comment.objects.create(body="test2", author=self.user, post=post)
        Comment.objects.create(body="test3", author=self.user, post=post)
        self.assertEqual(post.comments_count, 3)

    def test_post_tagged_count(self):
        #Check initial value of tagged_count
        Post.objects.create(title="test1", body="test1", author=self.user)
        post = Post.objects.get(title="test1")
        post.save()
        self.assertEqual(post.tagged_count, 0)

        #Creating and tagging 6 users
        for i in range(6):
            user = User.objects.create_user(username=f"testuser{i}", password="testpassword")
            UserTag.objects.create(user=user, post=post)
        
        #Check if tagged_count is updated
        post.refresh_from_db()
        self.assertEqual(post.tagged_count, 6)

        #Delete a user
        user = User.objects.get(username="testuser1")
        user.delete()

        #Check if tagged_count is updated
        post.refresh_from_db()
        self.assertEqual(post.tagged_count, 5)

    def test_post_last_tag_date(self):
        #Check initial value of last_tag_date
        Post.objects.create(title="test1", body="test1", author=self.user)
        post = Post.objects.get(title="test1")
        post.save()
        self.assertEqual(post.last_tag_date, None)

        #Creating and tagging 6 users
        for i in range(6):
            user = User.objects.create_user(username=f"testuser{i}", password="testpassword")
            UserTag.objects.create(user=user, post=post)
        
        #Check if last_tag_date is updated
        post.refresh_from_db()
        last_tag_date = post.usertag_set.last().created_at if post.usertag_set.exists() else None
        self.assertEqual(post.last_tag_date, last_tag_date)

@pytest.mark.django_db
class CommentTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(username="testuser", password="testpassword")
        self.user = User.objects.get(username="testuser")
        Post.objects.create(title="test1", body="test1", author=self.user)
        self.post = Post.objects.get(title="test1")

    def test_comment_character_limit(self):
        content = "x"*256
        with self.assertRaises(DataError):
            Comment.objects.create(body=content, author=self.user, post=self.post).full_clean()
    
    def test_comment_null_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(body=None, author=self.user, post=self.post).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(body="test", author=self.user, post=None).full_clean()  

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
        user = User.objects.get(username='testuser')
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
        self.user = User.objects.get(username="testuser")
        self.media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.media_root

    def tearDown(self):
        shutil.rmtree(self.media_root)

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
            'body': 'testing',
            'safe': False,
        })

        #Checking if response is OK
        self.assertEqual(response.status_code, 201)

        #Checking if the response is the same as the database
        post = Post.objects.get(title="testing")
        self.assertEqual(post.title, response.data['title'])
        self.assertEqual(post.body, response.data['body'])
        self.assertEqual(post.author.username, response.data['author'])
        self.assertEqual(post.safe, response.data['safe'])
        self.assertEqual(post.img.name,'')
        self.assertIsNotNone(post.created_at)
        self.assertIsNone(response.data['last_tag_date'])
        self.assertEqual(post.comments_count, 0)
        self.assertEqual(post.tagged_count, 0)

    def test_post_retrieve(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)

        #Getting the pk of the post
        post = Post.objects.first();

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-detail', kwargs={'pk':post.pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)
        
        #Checking if the response is the same as the database
        self.assertEqual(post.title, response.data['title'])
        self.assertEqual(post.body, response.data['body'])
        self.assertEqual(post.author.username, response.data['author'])
        self.assertEqual(post.safe, response.data['safe'])
        self.assertIsNone(response.data['img'])
        self.assertEqual(post.created_at, parse(response.data['created_at']))
        self.assertEqual(post.comments_count, response.data['comments_count'])
        self.assertEqual(post.tagged_count, response.data['tagged_count'])
        self.assertEqual(post.last_tag_date, response.data['last_tag_date'])

        image = SimpleUploadedFile("test_retrieve.jpg", b'file_content', content_type="image/jpeg")

        post.img = image
        post.save()
        post.refresh_from_db()

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-detail', kwargs={'pk':post.pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        self.assertRegex(response.data['img'], fr'^http://testserver/{post.img.name}$')
    
    def test_post_patch(self):
        #Force authentication
        self.client.force_authenticate(user=self.user)
        
        #Creating a image
        image = None
        with open('blog/static/images/test.png','rb') as f:
            image_data = f.read()
            image = SimpleUploadedFile('test_patch.png', image_data, content_type='image/png')

        #Getting the pk of the post
        post = Post.objects.first();

        #Getting the response from the API
        response = self.client.patch(reverse('blog:post-detail', kwargs={'pk':post.pk}),{
            'title': 'testing',
            'body': 'testing',
            'safe': False,
            'img': image
        })

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the databaset
        post = Post.objects.get(pk=post.pk);
        self.assertEqual(post.title, response.data['title'])
        self.assertEqual(post.body, response.data['body'])
        self.assertEqual(post.author.username, response.data['author'])
        self.assertEqual(post.safe, response.data['safe'])
        self.assertRegex(response.data['img'], fr'^http://testserver/{post.img.name}$')
        self.assertEqual(post.comments_count,response.data['comments_count'])
    
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
        response = self.client.get(reverse('blog:comment-list'))
        
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
        response = self.client.get(reverse('blog:comment-list'))
        
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
        comment = Comment.objects.get(body="testing")
        self.assertEqual(comment.body, response.data['body'])
        self.assertEqual(comment.author.pk, response.data['author'])
    
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
        self.assertEqual(self.comment.created_at, parse(response.data['created_at']))

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

@pytest.mark.django_db
class UserTagAPITest(APITestCase):

    def setUp(self):
        self.users = [User.objects.create_user(username=f"testuser{i}", password="testpassword") for i in range(1,6) ]
        self.posts = [Post.objects.create(title=f"test{i}", body=f"test{i}", author=self.users[i-1]) for i in range(1,6)]
    
    def test_usertag_create(self):
        #Force authentication
        self.client.force_authenticate(user=self.users[0])
        #Getting the response from the API to create usertag
        response = self.client.post(reverse('blog:usertag-list'),{
            'user': self.users[1].pk,
            'post': self.posts[0].pk
        })
        
        #Checking if response is OK
        self.assertEqual(response.status_code, 201)

        #Checking if the response is the same as the database
        usertag = UserTag.objects.get(user=self.users[1], post=self.posts[0])
        self.assertEqual(usertag.user.pk, response.data['user'])
        self.assertEqual(usertag.post.pk, response.data['post'])

    def test_usertag_users(self):
        #Force authentication
        self.client.force_authenticate(user=self.users[0])
        #Creating new usertags for the first post
        UserTag.objects.create(user=self.users[1], post=self.posts[0])

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-tagged-users',kwargs={'pk':self.posts[0].pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = UserTag.objects.count()
        self.assertEqual(count, response.data['count'])

        #Creating new usertags
        UserTag.objects.create(user=self.users[2], post=self.posts[0])
        UserTag.objects.create(user=self.users[3], post=self.posts[0])
        UserTag.objects.create(user=self.users[4], post=self.posts[0])

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-tagged-users',kwargs={'pk':self.posts[0].pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = UserTag.objects.count()
        self.assertEqual(count, response.data['count'])

    def test_usertag_posts(self):
        #Force authentication
        self.client.force_authenticate(user=self.users[0])
        #Creating new usertags for the first post
        UserTag.objects.create(user=self.users[1], post=self.posts[0])

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-tagged-posts',kwargs={'pk':self.users[1].pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = UserTag.objects.filter(user=self.users[1]).count()
        self.assertEqual(count, response.data['count'])

        #Creating new usertags
        UserTag.objects.create(user=self.users[1], post=self.posts[2])
        UserTag.objects.create(user=self.users[1], post=self.posts[3])
        UserTag.objects.create(user=self.users[1], post=self.posts[4])

        #Getting the response from the API
        response = self.client.get(reverse('blog:post-tagged-posts',kwargs={'pk':self.users[1].pk}))

        #Checking if response is OK
        self.assertEqual(response.status_code, 200)

        #Checking if the response is the same as the database
        count = UserTag.objects.filter(user=self.users[1]).count()
        self.assertEqual(count, response.data['count'])