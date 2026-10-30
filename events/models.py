import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# Event
# ─────────────────────────────────────────────
class Event(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="events"
    )
    description = models.TextField()
    location = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.PositiveIntegerField(default=100)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date"]
        indexes = [
            models.Index(fields=["is_published", "event_date"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title

    @property
    def booked_seats(self):
        result = (
            self.bookings.filter(status="confirmed")
            .values_list("seats", flat=True)
        )
        return sum(result) if result else 0

    @property
    def available_seats(self):
        return max(0, self.total_seats - self.booked_seats)

    @property
    def is_upcoming(self):
        return self.event_date >= timezone.now()

    @property
    def is_full(self):
        return self.available_seats <= 0


# ─────────────────────────────────────────────
# Booking
# ─────────────────────────────────────────────
class Booking(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    reference = models.CharField(
        max_length=20, unique=True, editable=False, db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_bookings",
    )
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="bookings"
    )
    seats = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="confirmed"
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-booked_at"]

    def __str__(self):
        return f"{self.reference} — {self.user.username} / {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "BK" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.seats * self.event.price


# ─────────────────────────────────────────────
# Tour Enquiry
# ─────────────────────────────────────────────
class TourEnquiry(models.Model):
    """Persisted venue tour enquiry submitted via the book-a-tour form."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    EVENT_TYPE_CHOICES = [
        ("Wedding + Reception", "Wedding + Reception"),
        ("Reception", "Reception"),
        ("Birthday Celebration", "Birthday Celebration"),
        ("Bridal Shower", "Bridal Shower"),
        ("Baby Shower", "Baby Shower"),
        ("Corporate Event", "Corporate Event"),
        ("Other", "Other"),
    ]

    EXPERIENCE_CHOICES = [
        ("Venue Rental", "Venue Rental"),
        ("Venue + Décor", "Venue + Décor"),
        ("Full service", "Full Service Event Experience"),
        ("Not sure", "Not Sure Yet"),
    ]

    INVESTMENT_CHOICES = [
        ("$3,500-$5,000", "$3,500 – $5,000"),
        ("$5000-$7,500", "$5,000 – $7,500"),
        ("$7,500-$10,000", "$7,500 – $10,000"),
        ("$10,000+", "$10,000+"),
    ]

    SOURCE_CHOICES = [
        ("Instagram", "Instagram"),
        ("TikTok", "TikTok"),
        ("Facebook", "Facebook"),
        ("Google", "Google"),
        ("Referral", "Referral"),
        ("Other", "Other"),
    ]

    # Reference
    reference = models.CharField(
        max_length=20, unique=True, editable=False, db_index=True
    )

    # Contact
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    # Event details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    event_date = models.DateField()
    date_flexible = models.BooleanField(default=False)
    guest_count = models.PositiveIntegerField()
    setup_works = models.CharField(max_length=30, blank=True)

    # Preferences
    experience = models.CharField(
        max_length=30, choices=EXPERIENCE_CHOICES, blank=True
    )
    investment_range = models.CharField(
        max_length=30, choices=INVESTMENT_CHOICES, blank=True
    )
    vision = models.TextField(blank=True)
    hear_about = models.CharField(max_length=30, choices=SOURCE_CHOICES, blank=True)
    ready_for_tour = models.CharField(max_length=20, blank=True)

    # Tour scheduling (optional)
    tour_datetime = models.CharField(max_length=100, blank=True)

    # Consent
    sms_consent = models.BooleanField(default=False)

    # Staff management
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", db_index=True
    )
    staff_notes = models.TextField(blank=True)

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Tour Enquiry"
        verbose_name_plural = "Tour Enquiries"
        indexes = [
            models.Index(fields=["status", "submitted_at"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.full_name} ({self.event_type})"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "TQ" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)