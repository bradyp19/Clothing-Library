from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from closet.models import BorrowRequest

class Command(BaseCommand):
    help = 'Send email reminders for borrowed items due soon.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)

        due_soon = BorrowRequest.objects.filter(
            borrow_end_date=tomorrow,
            status='APPROVED'
        )

        for borrow in due_soon:
            user_email = borrow.requester.email
            item_name = borrow.item.item_name
            due_date = borrow.end_date.strftime("%B %d, %Y")

            if user_email:
                send_mail(
                    subject='Reminder: Return Your Borrowed Item Tomorrow',
                    message=f"Hello {borrow.requester.username},\n\nThis is a reminder that your borrowed item \"{item_name}\" is due for return tomorrow ({due_date}).\n\nPlease make sure to return it on time.\n\nThank you!",
                    from_email='noreply@closetapp.com',  
                    recipient_list=[user_email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Sent reminder to {user_email} for {item_name}"))
