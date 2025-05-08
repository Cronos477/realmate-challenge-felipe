from django.db import models

class Conversation(models.Model):
    CONVERSATION_STATUS = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    
    id = models.CharField(max_length=255, unique=True, primary_key=True)
    status = models.CharField(max_length=6, choices=CONVERSATION_STATUS, default='OPEN')
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):
    DIRECTIONS = [
        ('RECEIVED', 'Received'),
        ('SENT', 'Sent'),
    ]
    
    message_id = models.CharField(max_length=255, unique=True)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    direction = models.CharField(max_length=8, choices=DIRECTIONS )
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Message {self.id}"
