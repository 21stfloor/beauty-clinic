from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import django_tables2 as tables
from .models import Appointment, Purpose, Service, Status
from django.core import serializers


class AppointmentTable(tables.Table):

    class Meta:
        orderable = False
        model = Appointment
        template_name = "django_tables2/bootstrap.html"
        fields = ("date", "service", "status", )
        attrs = {'class': 'table table-hover shadow records-table'}
        row_attrs = {'data-bs-toggle':"modal", 'data-bs-target':"#exampleModal", 'data-bs-appointment': lambda record: serializers.serialize('json', [ record, ])}
        # row_attrs = {
        #     "onClick": lambda record: f"document.location.href='{reverse('system:order-detail', kwargs={'pk': record.pk})}';"
        # }

    # def render_service(self, value, record):
    #     return Service(record.service).label
    
    def render_status(self, value, record):
        return Status(record.status).label