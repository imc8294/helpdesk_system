
from django.urls import path
from .views import TicketView, TicketAdminUpdateView, TicketAgentUpdateView, CommentsView
from .ticket_filter_view import FilteredTicketView, TicketReportingView

urlpatterns = [
    path('', TicketView.as_view(), name='tickets-list'),
    path('AdminUpdate/<int:ticket_id>', TicketAdminUpdateView.as_view(), name='Admin-tickets-update'),
    path('AgentUpdate/<int:ticket_id>', TicketAgentUpdateView.as_view(), name='agent-tickets-update'),
    path('Comment/<int:ticket_id>', CommentsView.as_view(), name='ticket-comment'),
    path('Filter', FilteredTicketView.as_view(), name='filtered-tickets'),
    path('Report', TicketReportingView.as_view(), name='ticket-report'),
]
