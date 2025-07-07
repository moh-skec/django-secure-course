import base64
import re
from cryptography.fernet import Fernet

from unittest.mock import patch

from celery.exceptions import Retry
import django.test
from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import TestCase

from api.utils import create_access_token, auth_header
from api.models import ActivityLog
from ugc.models import Comment, Journal
from ugc.tasks import create_comment


class CreateCommentTaskTestCase(TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_creates_object(self):
        self.assertEqual(Comment.objects.count(), 0)
        user, _ = User.objects.get_or_create(username='test_user')
        user_id = user.id
        cache_key = '{}/comment_created'.format(user_id)

        self.assertFalse(cache.has_key(cache_key))
        create_comment.run(user_id, 'example')
        comment = Comment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.text, 'example')  # type: ignore
        self.assertEqual(cache.get(cache_key), comment.id)  # type: ignore

    @patch('ugc.tasks.create_comment.retry')
    def test_retry(self, create_comment_retry):
        user, _ = User.objects.get_or_create(username='test_user_retry')
        user_id = user.id
        create_comment.run(user_id, 'example')
        create_comment_retry.side_effect = Retry()
        with self.assertRaises(Retry):
            create_comment.run(user_id, 'example')


class JournalTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='user', email='user@localhost'
        )
        self.auth_user = auth_header(create_access_token(self.user))

        self.other_user = User.objects.create(
            username='other_user', email='other_user@localhost'
        )
        self.auth_other_user = auth_header(
            create_access_token(self.other_user))
        Journal.objects.create(
            created_by=self.other_user, encrypted_text='hello-world'
        )

    def test_retrieve(self):
        journal = Journal.objects.create(
            created_by=self.user, encrypted_text='plaintext'
        )
        response = self.client.get(
            '/api/v1/journal/{}/'.format(journal.id),
            **self.auth_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': journal.id,
            'created_by': self.user.id,
            'encrypted_text': 'plaintext',
        })

    def test_list(self):
        journal = Journal.objects.create(
            created_by=self.user, encrypted_text='plaintext'
        )
        response = self.client.get('/api/v1/journal/', **self.auth_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{
                'id': journal.id,
                'created_by': self.user.id,
                'encrypted_text': 'plaintext',
            }]
        )

    def test_create(self):
        client_side_key = 'incredible2amazing'
        client_side_key += ('_' * (32 - len(client_side_key)))
        client_side_key = base64.urlsafe_b64encode(
            client_side_key.encode()
        )
        plain_text = 'hello world'.encode()
        encrypted_text = Fernet(client_side_key).encrypt(plain_text)
        encrypted_text = ''.join([chr(c) for c in encrypted_text])
        data = {
            'created_by': self.user.id,
            'encrypted_text': encrypted_text,
        }
        response = self.client.post(
            '/api/v1/journal/',
            data=data, **self.auth_user
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ActivityLog.objects.count(), 0)
        journal = Journal.objects.last()
        self.assertIsNotNone(journal)
        self.assertEqual(journal.created_by, self.user)  # type: ignore
        self.assertEqual(journal.encrypted_text, encrypted_text)  # type: ignore
        encrypted_bytes = bytes([ord(n) for n in journal.encrypted_text])  # type: ignore
        decrypted = Fernet(client_side_key).decrypt(encrypted_bytes)
        self.assertEqual(decrypted, b'hello world')


class JournalDeleteTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='user', email='user@localhost'
        )

    def test_csrf_token(self):
        journal_entry = Journal.objects.create(
            created_by=self.user, encrypted_text='plaintext'
        )
        client = django.test.Client(enforce_csrf_checks=True)
        response = client.post(
            '/journal/',
            {'entry_to_delete': journal_entry.id}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Journal.objects.count(), 1)

        response = client.get('/journal/')
        self.assertEqual(response.status_code, 200)

        csrf_match = re.search(
            'name="csrfmiddlewaretoken" value="(.*?)"',
            str(response.content)
        )
        self.assertIsNotNone(csrf_match)
        csrf_token = csrf_match[1]  # type: ignore
        response = client.post(
            '/journal/',
            {
                'entry_to_delete': journal_entry.id,
                'csrfmiddlewaretoken': csrf_token,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Journal.objects.count(), 0)
