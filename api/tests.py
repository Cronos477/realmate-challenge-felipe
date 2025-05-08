from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import Conversation, Message
from django.utils import timezone
import uuid

class WebhookHandlerTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.webhook_url = reverse('webhook')

    def test_new_conversation_handler_success(self):
        conversation_id = str(uuid.uuid4())
        data = {
            'type': 'NEW_CONVERSATION',
            'data': {
                'id': conversation_id
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Conversation.objects.filter(id=conversation_id).exists())
        conversation = Conversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.status, 'OPEN')

    def test_new_conversation_handler_missing_id(self):
        data = {
            'type': 'NEW_CONVERSATION',
            'data': {},
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No conversation ID provided')

    def test_new_conversation_handler_already_exists(self):
        conversation_id = str(uuid.uuid4())
        Conversation.objects.create(id=conversation_id, created_at=timezone.now())
        data = {
            'type': 'NEW_CONVERSATION',
            'data': {
                'id': conversation_id
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Conversation already exists')

    def test_close_conversation_handler_success(self):
        conversation_id = str(uuid.uuid4())
        Conversation.objects.create(id=conversation_id, created_at=timezone.now(), status='OPEN')
        data = {
            'type': 'CLOSE_CONVERSATION',
            'data': {
                'id': conversation_id
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        conversation = Conversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.status, 'CLOSED')
        self.assertIsNotNone(conversation.closed_at)

    def test_close_conversation_handler_not_found(self):
        conversation_id = str(uuid.uuid4())
        data = {
            'type': 'CLOSE_CONVERSATION',
            'data': {
                'id': conversation_id
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Conversation not found')

    def test_close_conversation_handler_already_closed(self):
        conversation_id = str(uuid.uuid4())
        Conversation.objects.create(id=conversation_id, created_at=timezone.now(), status='CLOSED', closed_at=timezone.now())
        data = {
            'type': 'CLOSE_CONVERSATION',
            'data': {
                'id': conversation_id
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Conversation is already closed.')

    def test_new_message_handler_success(self):
        conversation_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        Conversation.objects.create(id=conversation_id, created_at=timezone.now(), status='OPEN')
        data = {
            'type': 'NEW_MESSAGE',
            'data': {
                'id': message_id,
                'conversation_id': conversation_id,
                'direction': 'RECEIVED',
                'content': 'Hello there!'
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(message_id=message_id).exists())
        message = Message.objects.get(message_id=message_id)
        self.assertEqual(message.conversation.id, conversation_id)
        self.assertEqual(message.content, 'Hello there!')

    def test_new_message_handler_conversation_not_found(self):
        conversation_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        data = {
            'type': 'NEW_MESSAGE',
            'data': {
                'id': message_id,
                'conversation_id': conversation_id,
                'direction': 'RECEIVED',
                'content': 'Hello there!'
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Conversation not found')

    def test_new_message_handler_conversation_closed(self):
        conversation_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        Conversation.objects.create(id=conversation_id, created_at=timezone.now(), status='CLOSED', closed_at=timezone.now())
        data = {
            'type': 'NEW_MESSAGE',
            'data': {
                'id': message_id,
                'conversation_id': conversation_id,
                'direction': 'RECEIVED',
                'content': 'Hello there!'
            },
            'timestamp': timezone.now().isoformat()
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Conversation is already closed and cannot receive new messages.')

    def test_webhook_invalid_event_type(self):
        data = {'type': 'INVALID_EVENT', 'data': {}, 'timestamp': timezone.now().isoformat()}
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_invalid_body(self):
        data = {'invalid_key': 'some_value'}
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid request body')

    def test_webhook_invalid_method(self):
        response = self.client.get(self.webhook_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ConversationViewsetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.conv1 = Conversation.objects.create(id=str(uuid.uuid4()), created_at=timezone.now())
        self.conv2 = Conversation.objects.create(id=str(uuid.uuid4()), created_at=timezone.now())
        self.msg1_conv1 = Message.objects.create(message_id=str(uuid.uuid4()), conversation=self.conv1, direction='RECEIVED', content='Hi', timestamp=timezone.now())
        self.msg2_conv1 = Message.objects.create(message_id=str(uuid.uuid4()), conversation=self.conv1, direction='SENT', content='Hello', timestamp=timezone.now())

    def test_list_conversations(self):
        url = reverse('Conversations-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_conversation_with_messages(self):
        url = reverse('Conversations-detail', kwargs={'pk': self.conv1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.conv1.id)
        self.assertIn('messages', response.data)
        self.assertEqual(len(response.data['messages']), 2)
        self.assertEqual(response.data['messages'][0]['content'], self.msg2_conv1.content)
        self.assertEqual(response.data['messages'][1]['content'], self.msg1_conv1.content)

    def test_retrieve_conversation_not_found(self):
        url = reverse('Conversations-detail', kwargs={'pk': str(uuid.uuid4())})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
