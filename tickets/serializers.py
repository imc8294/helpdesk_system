from rest_framework import serializers
from .models import Ticket, Comments

class CommentsSerializer(serializers.ModelSerializer):
    commented_by = serializers.CharField(source='user.first_name', read_only=True)
    class Meta:
        model = Comments
        fields = ['id', 'comments', 'user', 'created_at', 'ticket', 'commented_by']


class TicketSerializer(serializers.ModelSerializer):
    comments = CommentsSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.first_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.first_name', read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_by', 'assigned_to', 'resolved_time', 'assigned_time', 'status']

    def validate(self, data):
        if data.get('priority') not in ['low', 'medium', 'high']:
            raise serializers.ValidationError("Priority must be 'low', 'medium', or 'high'.")
        if not data.get('title'):
            raise serializers.ValidationError("Tittle is required.")
        if not data.get('description'):
            raise serializers.ValidationError("Description is required.")

        return data
    
class TicketAdminSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_by', 'resolved_time', 'assigned_time']

    def validate(self, data):
        if data.get('priority') not in ['low', 'medium', 'high']:
            raise serializers.ValidationError("Priority must be 'low', 'medium', or 'high'.")
        if not data.get('title'):
            raise serializers.ValidationError("Tittle is required.")
        if not data.get('description'):
            raise serializers.ValidationError("Description is required.")

        return data
    
    def update_comment(request_data, ticket_instance, user_data):
        comment_text = request_data.get('comment')
        if comment_text:
            Comments.objects.create(ticket=ticket_instance, user=user_data, comments=comment_text)

        return ticket_instance
    
class TicketAgentSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Ticket
        fields = ['status', 'comment']
    
    def update_comment(request_data, ticket_instance, user_data):
        comment_text = request_data.get('comment')
        if comment_text:
            Comments.objects.create(ticket=ticket_instance, user=user_data, comments=comment_text)

        return ticket_instance