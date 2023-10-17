from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Appointment, ArchivedFile, CustomUser, create_archived_file

@receiver(user_logged_in, sender=CustomUser)
def archive_on_admin_login(sender, request, user, **kwargs):
    if user.is_superuser:  # Check if the user is an admin user
        appointments_to_archive = Appointment.objects.filter(archive=True)
        for appointment in appointments_to_archive:
            appointment.archived = True
            appointment.save()
            # ArchivedFile.archive_appointment(appointment)
