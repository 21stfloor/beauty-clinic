from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta
from app.models import Appointment
from beauty_clinic import settings

class Command(BaseCommand):
    help = 'Send email reminders for upcoming appointments one day before the appointment.'

    def handle(self, *args, **options):
        tomorrow = datetime.now() + timedelta(days=1)
        # Adjust the time to the beginning of the day
        tomorrow_start = datetime(tomorrow.year, tomorrow.month, tomorrow.day)

        # Calculate the end of the day (23:59:59)
        tomorrow_end = tomorrow_start + timedelta(days=1) - timedelta(seconds=1)

        # Filter for appointments within the date range
        upcoming_appointments = Appointment.objects.filter(date__range=(tomorrow_start, tomorrow_end))

        for appointment in upcoming_appointments:
            user = appointment.customer  # Assuming there is a ForeignKey field 'user' in the Appointment model
            subject = 'Upcoming Appointment Reminder'
            message = f'Your appointment is scheduled for tomorrow at {appointment.date}.\n For {appointment.service}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            # Send the reminder email
            send_mail(subject, message, from_email, recipient_list)

            self.stdout.write(self.style.SUCCESS(f'Sent a reminder to {user.firstname} {user.lastname} at {user.email}'))
