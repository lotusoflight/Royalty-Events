"""Royalty Events — Django Admin Configuration"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Booking, Category, Event, TourEnquiry

admin.site.site_header = "Royalty Events Administration"
admin.site.site_title = "Royalty Events Admin"
admin.site.index_title = "Welcome to Royalty Events Admin"


# ─────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_count", "description")
    search_fields = ("name",)

    def event_count(self, obj):
        # Fixed: use the correct related_name 'events' (not event_set)
        return obj.events.count()

    event_count.short_description = "Events"


# ─────────────────────────────────────────────
# Event
# ─────────────────────────────────────────────
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "location",
        "event_date",
        "price",
        "total_seats",
        "available_seats_display",
        "is_published",
        "created_at",
    )
    list_filter = ("category", "is_published", "event_date")
    search_fields = ("title", "location", "description")
    list_editable = ("is_published", "price")
    readonly_fields = ("created_at", "updated_at", "booked_seats_display")
    list_per_page = 20
    ordering = ("-created_at",)
    date_hierarchy = "event_date"

    fieldsets = (
        ("Event Details", {"fields": ("title", "category", "description", "location")}),
        ("Date & Pricing", {"fields": ("event_date", "price", "total_seats", "booked_seats_display")}),
        ("Media", {"fields": ("image",)}),
        ("Status & Metadata", {"fields": ("is_published", "created_by", "created_at", "updated_at")}),
    )

    def available_seats_display(self, obj):
        avail = obj.available_seats
        color = "green" if avail > 0 else "red"
        return format_html('<span style="color:{}">{}</span>', color, avail)

    available_seats_display.short_description = "Available"

    def booked_seats_display(self, obj):
        return obj.booked_seats

    booked_seats_display.short_description = "Booked Seats"


# ─────────────────────────────────────────────
# Booking
# ─────────────────────────────────────────────
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "event",
        "seats",
        "total_price",
        "status",
        "booked_at",
    )
    list_filter = ("status", "booked_at", "event__category")
    search_fields = ("reference", "user__username", "user__email", "event__title")
    readonly_fields = ("reference", "booked_at", "updated_at", "total_price")
    list_editable = ("status",)
    list_per_page = 25
    ordering = ("-booked_at",)
    date_hierarchy = "booked_at"


# ─────────────────────────────────────────────
# Tour Enquiry
# ─────────────────────────────────────────────
@admin.register(TourEnquiry)
class TourEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "full_name",
        "email",
        "phone",
        "event_type",
        "event_date",
        "guest_count",
        "status",
        "submitted_at",
    )
    list_filter = ("status", "event_type", "submitted_at", "experience")
    search_fields = ("reference", "full_name", "email", "phone")
    list_editable = ("status",)
    readonly_fields = ("reference", "submitted_at", "updated_at")
    list_per_page = 25
    ordering = ("-submitted_at",)
    date_hierarchy = "submitted_at"

    fieldsets = (
        ("Reference", {"fields": ("reference", "status", "staff_notes")}),
        (
            "Contact Information",
            {"fields": ("full_name", "email", "phone", "sms_consent")},
        ),
        (
            "Event Details",
            {
                "fields": (
                    "event_type",
                    "event_date",
                    "date_flexible",
                    "guest_count",
                    "setup_works",
                )
            },
        ),
        (
            "Preferences",
            {
                "fields": (
                    "experience",
                    "investment_range",
                    "vision",
                    "hear_about",
                    "ready_for_tour",
                    "tour_datetime",
                )
            },
        ),
        ("Timestamps", {"fields": ("submitted_at", "updated_at")}),
    )