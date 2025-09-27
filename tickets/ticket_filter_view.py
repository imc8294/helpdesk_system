from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer
from .ticket_helper import TicketHelper
from users.models import CustomUser
from datetime import timedelta, datetime

class FilteredTicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    ticket_helper = TicketHelper()

    @swagger_auto_schema(
        operation_summary="Filter tickets based on status, assigned_to, title, and priority.",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Serach by status (open, in-progress, resolved, escalated, closed)",
                type=openapi.TYPE_STRING,
                enum=['open', 'in-progress', 'resolved', 'escalated', 'closed']
            ),
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="Serach by title",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'priority',
                openapi.IN_QUERY,
                description="Serach by priority (low, medium, high)",
                type=openapi.TYPE_STRING,
                enum=['low', 'medium', 'high']
            ),
            openapi.Parameter(
                'assigned_to',
                openapi.IN_QUERY,
                description="Serach by assigned_to (user id)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="Filtered tickets retrieved successfully",
                schema=TicketSerializer(many=True)
            ),
            400: "Bad Request",
            403: "You Don't Permission to view tickets",
        }
        )
    def get(self, request):
        user = request.user
        status = request.query_params.get('status')
        assigned_to = request.query_params.get('assigned_to')
        title = request.query_params.get('title')
        priority = request.query_params.get('priority')

        
        if self.ticket_helper.user_role(user) == 'user':
            tickets = Ticket.objects.filter(created_by=user)
        elif self.ticket_helper.user_role(user) == 'agent':
            tickets = Ticket.objects.filter(assigned_to=user)
        elif self.ticket_helper.user_role(user) == 'admin':
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.none()

        if status:
            tickets = tickets.filter(status=status)
        
        if assigned_to:
            try:
                assigned_user = CustomUser.objects.get(id=assigned_to)
                tickets = tickets.filter(assigned_to=assigned_user)
            except CustomUser.DoesNotExist:
                return Response({'error': 'Assigned user not found'}, status=404)
            
        if title:
            tickets = tickets.filter(title__icontains=title)
        
        if priority:
            if not priority in ['low', 'medium', 'high']:
                return Response({'error': 'Invalid priority value'}, status=400)
            tickets = tickets.filter(priority=priority)

        serializer = self.serializer_class(tickets, many=True)
        return Response(serializer.data)
    
class TicketReportingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    ticket_helper = TicketHelper()


    @swagger_auto_schema(
        operation_summary="Reporting of tickets based on their status and assignment of last 7 days.",
        responses={
            200: openapi.Response(
                description="Reporting of tickets based on their status and assignment of last 7 days.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'opened': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of opened tickets'),
                        'resolved': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of resolved tickets'),
                        'escalated': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of escalated tickets'),
                        'assigned': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of assigned tickets'),
                        'unassigned': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unassigned tickets'),
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of tickets'),
                    }
                )
            ),
            400: openapi.Response(description="Bad Request"),
            403: openapi.Response(description="You don't have permission to view tickets"),
        }
    )
    def get(self, request):
        user = request.user

        seven_days_ago = datetime.now() - timedelta(days=7)
        if self.ticket_helper.user_role(user) == 'user':
            tickets = Ticket.objects.filter(created_by=user, created_at__gte=seven_days_ago)
        elif self.ticket_helper.user_role(user) == 'agent':
            tickets = Ticket.objects.filter(assigned_to=user, created_at__gte=seven_days_ago)
        elif self.ticket_helper.user_role(user) == 'admin':
            tickets = Ticket.objects.filter(created_at__gte=seven_days_ago)
        else:
            tickets = Ticket.objects.none()

        report = {
            "opened": tickets.filter(status="open").count(),
            "resolved": tickets.filter(status="resolved").count(),
            "escalated": tickets.filter(status="escalated").count(),
            "assigned": tickets.filter(assigned_to__isnull=False).count(),
            "unassigned": tickets.filter(assigned_to__isnull=True).count(),
            "total": tickets.count()
        }
        return Response({
            "Description": "Reporting of tickets based on their status and assignment of last 7 days.",
            "report": report
        })
