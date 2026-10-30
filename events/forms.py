"""
Royalty Events — Forms
Server-side validation for all user-submitted data.
"""
from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Booking, Event, TourEnquiry


# ─────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "luxe-input", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "luxe-input", "placeholder": "Last name"}),
    )
    username = forms.CharField(
        max_length=30,
        min_length=3,
        required=True,
        help_text="Choose a unique username (3–30 characters).",
        widget=forms.TextInput(attrs={"class": "luxe-input", "placeholder": "Enter username"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "luxe-input", "placeholder": "Email address"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].help_text = "Choose a unique username (3–30 characters)."
            self.fields["username"].widget.attrs.update({
                "placeholder": "Enter username",
                "maxlength": "30",
            })
        if "password1" in self.fields:
            self.fields["password1"].help_text = "At least 6 characters."
            self.fields["password1"].widget.attrs.update({
                "placeholder": "Create password",
            })
        if "password2" in self.fields:
            self.fields["password2"].help_text = "Re-enter your password to confirm."
            self.fields["password2"].widget.attrs.update({
                "placeholder": "Confirm password",
            })
        for name, field in self.fields.items():
            if not hasattr(field.widget, "attrs"):
                continue
            field.widget.attrs.setdefault("class", "luxe-input")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters.")
        if len(username) > 30:
            raise forms.ValidationError("Username cannot exceed 30 characters.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email.lower()


# ─────────────────────────────────────────────
# Event management (staff only)
# ─────────────────────────────────────────────
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "category",
            "description",
            "location",
            "event_date",
            "price",
            "total_seats",
            "image",
            "is_published",
        ]
        widgets = {
            "event_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "luxe-input"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 4, "class": "luxe-input", "placeholder": "Event details…"}
            ),
            "title": forms.TextInput(attrs={"class": "luxe-input", "placeholder": "Event title"}),
            "location": forms.TextInput(attrs={"class": "luxe-input", "placeholder": "Location"}),
            "price": forms.NumberInput(attrs={"class": "luxe-input", "min": 0, "step": "0.01"}),
            "total_seats": forms.NumberInput(attrs={"class": "luxe-input", "min": 1}),
        }

    def clean_event_date(self):
        event_date = self.cleaned_data["event_date"]
        if event_date <= timezone.now():
            raise forms.ValidationError("Event date must be in the future.")
        return event_date

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price


# ─────────────────────────────────────────────
# Event booking
# ─────────────────────────────────────────────
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["seats"]
        widgets = {
            "seats": forms.NumberInput(
                attrs={"min": 1, "max": 10, "class": "luxe-input", "placeholder": "Number of seats"}
            ),
        }

    def clean_seats(self):
        seats = self.cleaned_data["seats"]
        if seats < 1 or seats > 10:
            raise forms.ValidationError("You can book between 1 and 10 seats.")
        return seats


# ─────────────────────────────────────────────
# Tour Enquiry — the real form backed by TourEnquiry model
# ─────────────────────────────────────────────
class TourEnquiryForm(forms.ModelForm):
    """
    Validates and saves a venue tour enquiry.
    All server-side rules enforced — client HTML required attrs are supplementary.
    """

    class Meta:
        model = TourEnquiry
        fields = [
            "full_name",
            "email",
            "phone",
            "event_type",
            "setup_works",
            "event_date",
            "date_flexible",
            "guest_count",
            "experience",
            "investment_range",
            "vision",
            "hear_about",
            "ready_for_tour",
            "tour_datetime",
            "sms_consent",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "luxe-form-input", "placeholder": "Your full name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "luxe-form-input", "placeholder": "Email address"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "luxe-form-input", "placeholder": "Phone number"}
            ),
            "event_date": forms.DateInput(
                attrs={"type": "date", "class": "luxe-form-input"}
            ),
            "guest_count": forms.NumberInput(
                attrs={"class": "luxe-form-input", "min": 1, "max": 500,
                       "placeholder": "Estimated guest count (max 150)"}
            ),
            "vision": forms.Textarea(
                attrs={"class": "luxe-form-input", "rows": 4,
                       "placeholder": "Describe your desired style, colour palette, atmosphere…"}
            ),
            "tour_datetime": forms.TextInput(
                attrs={"class": "luxe-form-input", "placeholder": "Optional — preferred tour date & time"}
            ),
        }

    def clean_event_date(self):
        event_date = self.cleaned_data.get("event_date")
        if event_date and event_date <= date.today():
            raise forms.ValidationError("Please choose a future date for your event.")
        return event_date

    def clean_guest_count(self):
        count = self.cleaned_data.get("guest_count")
        if count is not None and count < 1:
            raise forms.ValidationError("Guest count must be at least 1.")
        if count is not None and count > 500:
            raise forms.ValidationError("Guest count cannot exceed 500.")
        return count

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 7:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name