from django.db import models
import uuid
from django.utils import timezone

class TrackingNumber(models.Model):
    # Fields for the tracking number details
    tracking_number = models.CharField(max_length=20, unique=True, db_index=True)
    origin_country_id = models.CharField(max_length=2)
    destination_country_id = models.CharField(max_length=2)
    weight = models.DecimalField(max_digits=6, decimal_places=3)
    created_at = models.DateTimeField(default=timezone.now)

    # Customer related fields
    customer_id = models.UUIDField(default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_slug = models.SlugField(max_length=255)

    def __str__(self):
        return self.tracking_number

    class Meta:
        # Optional: Constraints or ordering
        ordering = ['-created_at']
