from celery import shared_task
from django.utils.timezone import now
from django.core.mail import send_mail
from .models import Ticket
from users.models import CustomUser


@shared_task
def check_all_tickets_for_escalation():
    print("Checking tickets for escalation...")
    tickets = Ticket.objects.filter(status__in=['open', 'in-progress'])
    for ticket in tickets:
        print(f"Checking ticket ID: {ticket.id}")
        escalate_ticket.delay(ticket.id)

@shared_task
def escalate_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.status in ['resolved', 'closed', 'escalated']:
            return  'No escalation needed'

        total_time_taken_by_agent = (now() - ticket.updated_at).total_seconds()
        priority_time_rules = {
            'high': 3600,        # 1 hour
            'medium': 14400,     # 4 hours
            'low': 86400         # 24 hours
        }

        expected_time = priority_time_rules.get(ticket.priority)
        if expected_time and total_time_taken_by_agent > expected_time:
            ticket.status = 'escalated'
            ticket.save()

            recipients = [ticket.created_by.email]
            admins = CustomUser.objects.filter(is_staff=True).values_list('email', flat=True)
            recipients.extend(admins)

            return send_mail(
                subject='Ticket Escalation Alert for ticket #' + str(ticket.title),
                message=f'Ticket #{ticket.id} titled "{ticket.title}" has been escalated due to delay by agent.',
                from_email='noreply@varsityhelpdesk.com',
                recipient_list=recipients,
                fail_silently=True
            )
    except Ticket.DoesNotExist:
        pass
