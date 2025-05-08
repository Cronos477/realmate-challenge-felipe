from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from api.webhook_handler import *
from api.serializers import *
from api.models import *


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    http_method_names = ['get']

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        
        if not instance:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConversationSerializer(instance)

        data = serializer.data

        messages = Message.objects.filter(
            conversation=instance).order_by('-timestamp')
        message_serializer = MessageSerializer(messages, many=True)
        data['messages'] = message_serializer.data

        return Response(data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer
    http_method_names = ['get']


@api_view(['POST'])
def webhook(request):
    """
    Recebe o webhook da API e chama o manipulador apropriado.
    """
    if request.method == 'POST':
        body = request.data

        if not body or 'type' not in body:
            return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

        events = {
            'NEW_CONVERSATION': new_conversation_handler,
            'CLOSE_CONVERSATION': close_conversation_handler,
            'NEW_MESSAGE': new_message_handler
        }

        handler = events.get(body['type'])
        if not handler:
            return Response({'error': 'Invalid event type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verifica se o evento é de nova conversa
        response = handler(body)

        return response

    return Response({'error': 'Invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
