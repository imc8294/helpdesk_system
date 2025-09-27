from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Response as OpenApiResponse
from rest_framework import permissions
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer, TicketAdminSerializer, TicketAgentSerializer, CommentsSerializer
from .ticket_helper import TicketHelper
from users.models import CustomUser
from datetime import datetime
from rest_framework.generics import GenericAPIView

class TicketView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    ticket_helper = TicketHelper()

    @swagger_auto_schema(
        operation_summary="List all tickets . Users see their own tickets " \
        "agents see tickets assigned to them, and admins see all tickets.",
        responses={
            200: TicketSerializer(many=True),
            400: "Bad Request", 
            403: "Forbidden"
        }
    )
    def get(self, request):
        user = request.user
        
        if self.ticket_helper.user_role(user) == 'user':
            tickets = Ticket.objects.filter(created_by=user)
        elif self.ticket_helper.user_role(user) == 'agent':
            tickets = Ticket.objects.filter(assigned_to=user)
        elif self.ticket_helper.user_role(user) == 'admin':
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.none()
        
        serializer = self.serializer_class(tickets, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new ticket. Only users and admins can create tickets.",
        responses={201: "Ticket created successfully", 400: "Bad Request", 403: "You have not this permission"}
    )
    def post(self, request):
        user = request.user
        if not self.ticket_helper.check_admin_or_user(user):
            return Response({'error': 'You have not this permission'}, status=403)
        
        request.data['created_by'] = user.id
        request.data['status'] = 'open'
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Ticket created successfully', 
                'ticket': serializer.data
            }, status=201
            )
        return Response(serializer.errors, status=400)
    
    # @swagger_auto_schema(
    #     operation_summary="Update a ticket. Admins and agents can update tickets. " \
    #     "Admins can update any ticket, while agents can only update assigned tickets status.",
    #     responses={200: "Ticket updated successfully", 400: "Bad Request", 403: "You have not this permission", 404: "Ticket not found"}
    # )
    # def patch(self, request):
    #     user = request.user

    #     if not self.ticket_helper.check_admin_or_agent(user):
    #         return Response({'error': "You Don't Permission to update ticket"}, status=403)
        
    #     ticket_id = request.data.get('id')
    #     if not ticket_id:
    #         return Response({'error': 'Ticket ID is required'}, status=400)
        
    #     if user.is_staff or user.role == 'admin':
    #         try:
    #             ticket = Ticket.objects.get(id=ticket_id)
    #         except Ticket.DoesNotExist:
    #             return Response({'error': 'Ticket not found'}, status=404)
    #         if 'assigned_to' in request.data:
    #             try:
    #                 assigned_user = CustomUser.objects.get(id=request.data['assigned_to'], role='agent')
    #                 request.data['assigned_to'] = assigned_user.id
    #                 request.data['assigned_time'] = datetime.now()
    #             except CustomUser.DoesNotExist:
    #                 return Response({'error': 'Assigned user not found or not an agent'}, status=400)
    #         serializer = TicketSerializer(ticket, data=request.data, partial=True)
    #     else:
    #         try:
    #             ticket = Ticket.objects.get(id=ticket_id, assigned_to=user.id)
    #         except Ticket.DoesNotExist:
    #             return Response({'error': 'Ticket not found'}, status=404)
    #         if 'status' in request.data and request.data['status'] == 'resolved':
    #             request.data['resolved_time'] = datetime.now()
    #         allowed_fields = ['status']
    #         restricted_data = {field: request.data[field] for field in allowed_fields if field in request.data}
    #         serializer = TicketSerializer(ticket, data=restricted_data, partial=True)

        
        
        # if self.ticket_helper.check_admin_or_agent(user):
        #     serializer = self.serializer_class(ticket, data=request.data, partial=True)
        #     if serializer.is_valid():
        #         serializer.save()
        #         return Response({
        #             'message': 'Ticket updated successfully', 
        #             'ticket': serializer.data
        #         }, status=200)
        #     return Response(serializer.errors, status=400)
        # else:
        #     return Response({'error': 'You have not this permission'}, status=403)


class TicketAdminUpdateView(GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = TicketAdminSerializer
    ticket_helper = TicketHelper()

    @swagger_auto_schema(
        operation_summary="Admin can update any ticket.",
        responses={
            200: OpenApiResponse(
                description="Ticket updated successfully",
                schema=TicketAdminSerializer()
            ),
            400: "Bad Request",
            403: "You Don't Permission to update ticket",
            404: "Ticket not found"
        }
    )
    def patch(self, request, ticket_id):
        user = request.user

        if not self.ticket_helper.check_admin(user):
            return Response({'error': "You Don't Permission to update ticket"}, status=403)
        
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=404)
        
        if 'assigned_to' in request.data:
            try:
                assigned_user = CustomUser.objects.get(id=request.data['assigned_to'], role='agent')
                request.data['assigned_to'] = assigned_user.id
                request.data['assigned_time'] = datetime.now()
            except CustomUser.DoesNotExist:
                return Response({'error': 'Assigned user not found or not an agent'}, status=400)
        else:
            request.data['assigned_to'] = ticket.assigned_to 
            request.data['assigned_time'] = ticket.assigned_time

        if 'status' in request.data and request.data['status'] == 'resolved' and ticket.status != 'resolved':
            request.data['resolved_time'] = datetime.now()
        
        request.data['status'] = ticket.status if not request.data.get('status') else request.data['status']
        request.data['priority'] = ticket.priority if not request.data.get('priority') else request.data['priority']
        request.data['title'] = ticket.title if not request.data.get('title') else request.data['title']
        request.data['description'] = ticket.description if not request.data.get('description') else request['description']
        request.data['created_by'] = ticket.created_by
        request.data['created_at'] = ticket.created_at

        serializer = TicketSerializer(ticket, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            self.serializer_class.update_comment(request.data, ticket, user)
            return Response({
                'message': 'Ticket updated successfully', 
                'ticket': serializer.data
            }, status=200)
        return Response(serializer.errors, status=400)
    
    @swagger_auto_schema(
        operation_summary="Delete a ticket. Only admins can delete tickets.",
        responses={200: "Ticket deleted successfully", 400: "Bad Request", 403: "You have not this permission", 404: "Ticket not found"}
    )    
    def delete(self, request, ticket_id):
        user = request.user
        if not self.ticket_helper.check_admin(user):
            return Response({'error': 'You have not this permission'}, status=403)

        if not ticket_id:
            return Response({'error': 'Ticket ID is required'}, status=400)
        
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.delete()
            return Response({'message': 'Ticket deleted successfully'}, status=200)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=404)

class TicketAgentUpdateView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketAgentSerializer
    ticket_helper = TicketHelper()

    @swagger_auto_schema(
        operation_summary="Agent can update status and comment of assigned tickets only.",
        responses={
            200: OpenApiResponse(
                description="Ticket updated successfully",
                schema=TicketSerializer()
            ),
            400: "Bad Request",
            403: "You Don't Permission to update ticket",
            404: "Ticket not found"
        }
    )
    def patch(self, request, ticket_id):
        user = request.user

        if not self.ticket_helper.check_agent(user):
            return Response({'error': "You Don't Permission to update ticket"}, status=403)
        
        try:
            ticket = Ticket.objects.get(id=ticket_id, assigned_to=user.id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=404)
        
        if 'status' in request.data and request.data['status'] == 'resolved':
            request.data['resolved_time'] = datetime.now()
        
        allowed_fields = ['status']
        restricted_data = {field: request.data[field] for field in allowed_fields if field in request.data}
        restricted_data['priority'] = ticket.priority
        restricted_data['title'] = ticket.title
        restricted_data['description'] = ticket.description
        restricted_data['created_by'] = ticket.created_by
        restricted_data['assigned_to'] = ticket.assigned_to
        restricted_data['created_at'] = ticket.created_at
        restricted_data['assigned_time'] = ticket.assigned_time
        restricted_data['resolved_time'] = ticket.resolved_time

        serializer = TicketSerializer(ticket, data=restricted_data)

        if serializer.is_valid():
            serializer.save()
            self.serializer_class.update_comment(request.data, ticket, user)
            return Response({
                'message': 'Ticket updated successfully', 
                'ticket': serializer.data
            }, status=200)
        return Response(serializer.errors, status=400)

class CommentsView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentsSerializer
    ticket_helper = TicketHelper()


    @swagger_auto_schema(
        operation_summary="List comments for a specific ticket. Users see comments on their " \
        "own tickets agents see comments on tickets assigned to them, and admins see all comments.",
        responses={
            200: CommentsSerializer(many=True), 400: "Bad Request", 
            403: "Forbidden", 404: "Ticket not found or access denied"
        }
    )
    def get(self, request, ticket_id):
        user = request.user
        
        if not ticket_id:
            return Response({'error': 'Ticket ID is required'}, status=400)
        
        if self.ticket_helper.user_role(user) == 'user':
            tickets = Ticket.objects.filter(created_by=user)
        elif self.ticket_helper.user_role(user) == 'agent':
            tickets = Ticket.objects.filter(assigned_to=user)
        elif self.ticket_helper.user_role(user) == 'admin':
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.none()
        
        tickets = tickets.filter(id=ticket_id)
        if not tickets.exists():
            return Response({'error': 'Ticket not found or access denied'}, status=404)
        
        comments = tickets.first().comments.all()
        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data)