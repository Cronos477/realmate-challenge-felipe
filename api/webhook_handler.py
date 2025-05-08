from api.serializers import ConversationSerializer, MessageSerializer
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from api.models import Conversation, Message
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

def new_conversation_handler(body:dict):
    """
    Controla a criação de uma nova conversa.
    Recebe o corpo da requisição e cria uma nova conversa no banco de dados.
    """
    if not 'data' in body:
        return Response(
            {'error': 'Invalid request body'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not 'id' in body['data']:
        return Response(
            {'error': 'No conversation ID provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtém o ID da conversa do corpo da requisição
    conversation_id = body['data']['id']
    
    # Verifica se o ID da conversa foi fornecido e se já existe no banco de dados
    if not conversation_id:
        return Response(
            {'error': 'No conversation ID provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if Conversation.objects.filter(id=conversation_id).exists():
        return Response(
            {'error': 'Conversation already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cria um dicionário com os dados da nova conversa
    conversation_data = {
        'id': conversation_id,
        'status': 'OPEN',
        'created_at': body['timestamp'],
        'closed_at': None
    }
    
    serializer = ConversationSerializer(data=conversation_data)
    
    # Valida os dados da nova conversa
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Salva a nova conversa no banco de dados
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def close_conversation_handler(body:dict):
    """
    Controla o fechamento de uma conversa.
    Recebe o corpo da requisição e atualiza o status da conversa no banco de dados.
    """
    # Obtém o ID da conversa do corpo da requisição
    conversation_id = body['data']['id']
    
    # Verifica se o ID da conversa foi fornecido
    if not conversation_id:
        return Response(
            {'error': 'No conversation ID provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Busca a conversa no banco de dados
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
    except Http404:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if conversation.status == 'CLOSED':
        return Response(
            {'error': 'Conversation is already closed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Atualiza o status da conversa para 'CLOSED'
    conversation.status = 'CLOSED'
    conversation.closed_at = body['timestamp']
    
    # Salva as alterações no banco de dados
    conversation.save()
    
    return Response(model_to_dict(conversation), status=status.HTTP_200_OK)


def new_message_handler(body:dict):
    """
    Controla o recebimento de uma nova mensagem.
    Recebe o corpo da requisição e cria uma nova mensagem no banco de dados.
    """
    # Obtém o ID da conversa do corpo da requisição
    conversation_id = body['data']['conversation_id']
    
    # Verifica se o ID da conversa foi fornecido
    if not conversation_id:
        return Response(
            {'error': 'No conversation ID provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Busca a conversa no banco de dados
    conversation = Conversation.objects.filter(id=conversation_id)
    if not conversation.exists():
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Obtém a conversa correspondente
    conversation = conversation.get(id=conversation_id)
    
    if conversation.status == 'CLOSED':
        return Response(
            {'error': 'Conversation is already closed and cannot receive new messages.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cria um dicionário com os dados da nova mensagem
    message_data = {
        'message_id': body['data']['id'],
        'conversation': conversation_id,
        'direction': body['data']['direction'],
        'content': body['data']['content'],
        'timestamp': body['timestamp']
    }
    
    serializer = MessageSerializer(data=message_data)
    
    # Valida os dados da nova mensagem
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Salva a nova mensagem no banco de dados
    serializer.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)