from django.db import models
from users.models import CustomUser as User


class Ticket(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    STATUS_CHOICES = [('open', 'Open'), ('in-progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed'), ('escalated', 'Escalated')]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(User, related_name='created_tickets', on_delete=models.CASCADE, null=True)
    assigned_to = models.ForeignKey(User, related_name='assigned_tickets', null=True, blank=True, on_delete=models.SET_NULL)
    assigned_time = models.DateTimeField(null=True, blank=True)
    resolved_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey('Ticket', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment {self.id} on Ticket {self.ticket.id} by {self.author.username}'
