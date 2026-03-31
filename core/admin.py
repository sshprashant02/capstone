from django.contrib import admin
from .models import Cause, Donation, DonorProfile

admin.site.register(Cause)
admin.site.register(Donation)
admin.site.register(DonorProfile)
