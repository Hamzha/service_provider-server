from django.contrib import admin
from leads.models.service_category import ServiceCategory
from leads.models.job import Job
from leads.models.lead import Lead
from leads.models.service import Service
from leads.models.rating import Rating

admin.site.register(ServiceCategory)
admin.site.register(Job)
admin.site.register(Lead)
admin.site.register(Service)
admin.site.register(Rating)
