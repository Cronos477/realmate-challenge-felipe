from api.views import ConversationViewSet, webhook
from realmate_challenge.urls import router
from django.urls import path

router.register('conversations', ConversationViewSet, 'Conversations')

urlpatterns = [
    path('webhook/', webhook, name='webhook'),
]
