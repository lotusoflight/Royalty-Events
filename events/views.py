"""
Royalty Events — Views
All business logic lives here.
"""
import logging
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.conf import settings
from .models import Event, Category

from .forms import BookingForm, EventForm, RegisterForm, TourEnquiryForm
from .models import Booking, Category, Event, TourEnquiry

logger = logging.getLogger(__name__)

def _is_staff(user):
    return user.is_staff or user.is_superuser

def home(request):
    upcoming_events = Event.objects.filter(is_published=True, event_date__gte=timezone.now()).select_related("category")[:3]
    return render(request, "events/home.html", {"upcoming_events": upcoming_events, "featured_events": upcoming_events})

def all_events_api(request):
    events_qs = Event.objects.filter(is_published=True).order_by('-event_date')[:25]
    data = []
    for e in events_qs:
        data.append({
            'id': e.id,
            'title': e.title,
            'date': e.event_date.strftime('%Y-%m-%d %I:%M %p') if e.event_date else '',
            'location': getattr(e, 'location', 'Royalty Events, Houston'),
        })
    return JsonResponse(data, safe=False)

def the_venue(request): return render(request, "events/the_venue.html")
def weddings(request): return render(request, "events/weddings.html")
def celebrations(request): return render(request, "events/celebrations.html")
def gallery(request): return render(request, "events/gallery.html")
def tour_venue(request): return render(request, "events/tour_venue.html")

def book_tour(request):
    if request.method == "POST":
        form = TourEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            return redirect("book_tour_success", reference=enquiry.reference)
    else:
        form = TourEnquiryForm()
    return render(request, "events/book_tour.html", {"form": form})

def book_tour_success(request, reference):
    enquiry = get_object_or_404(TourEnquiry, reference=reference)
    return render(request, "events/book_tour_success.html", {"enquiry": enquiry})


def event_list(request):
    events = Event.objects.filter(is_published=True).order_by('-event_date')
    categories = Category.objects.all()
    active_category = request.GET.get('category')
    show_all = request.GET.get('all')

    if active_category:
        events = events.filter(category__name=active_category)

    # Normal ah 3, ALL EVENTS click panna 30
    per_page = 100 if show_all else 3
    paginator = Paginator(events, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'active_category': active_category,
        'show_all': show_all
    })
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    booking_form = BookingForm() if request.user.is_authenticated else None
    return render(request, "events/event_detail.html", {"event": event, "booking_form": booking_form})

@login_required
def book_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data["seats"]
            with transaction.atomic():
                fresh = Event.objects.select_for_update().get(pk=pk)
                booking = Booking.objects.create(user=request.user, event=fresh, seats=seats, status="confirmed")
            messages.success(request, f"Booking confirmed! {booking.reference}")
            return redirect("my_bookings")
    else:
        form = BookingForm()
    return render(request, "events/event_detail.html", {"event": event, "booking_form": form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("event").order_by("-booked_at")
    return render(request, "events/my_bookings.html", {"bookings": bookings})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.status = "cancelled"
    booking.save(update_fields=["status", "updated_at"])
    return redirect("my_bookings")

def register(request):
    if request.user.is_authenticated: return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "events/register.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
@user_passes_test(_is_staff, login_url="login")
def dashboard(request):
    now = timezone.now()
    ctx = {
        "total_events": Event.objects.count(),
        "published_events": Event.objects.filter(is_published=True).count(),
        "upcoming_events": Event.objects.filter(is_published=True, event_date__gte=now).count(),
        "total_enquiries": TourEnquiry.objects.count(),
        "new_enquiries": TourEnquiry.objects.filter(status="new").count(),
        "total_bookings": Booking.objects.count(),
        "confirmed_bookings": Booking.objects.filter(status="confirmed").count(),
        "recent_enquiries": TourEnquiry.objects.order_by("-submitted_at")[:10],
        "recent_bookings": Booking.objects.select_related("user", "event").order_by("-booked_at")[:10],
    }
    return render(request, "events/dashboard.html", ctx)

@login_required
@user_passes_test(_is_staff, login_url="login")
def staff_enquiries(request):
    qs = TourEnquiry.objects.all().order_by('-submitted_at')
    status_filter = request.GET.get("status", "")
    if status_filter:
        qs = qs.filter(status=status_filter)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "events/staff_enquiries.html", {"page_obj": page_obj, "status_filter": status_filter, "status_choices": TourEnquiry.STATUS_CHOICES})

@login_required
@user_passes_test(_is_staff, login_url="login")
def enquiry_detail(request, pk):
    enquiry = get_object_or_404(TourEnquiry, pk=pk)
    if request.method == "POST":
        enquiry.status = request.POST.get("status", enquiry.status)
        enquiry.staff_notes = request.POST.get("staff_notes", "")
        enquiry.save(update_fields=["status", "staff_notes", "updated_at"])
        messages.success(request, "Enquiry updated.")
        return redirect("enquiry_detail", pk=pk)
    return render(request, "events/enquiry_detail.html", {"enquiry": enquiry})

@login_required
@user_passes_test(_is_staff, login_url="login")
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect("event_detail", pk=event.pk)
    else:
        form = EventForm()
    return render(request, "events/event_form.html", {"form": form, "action": "Create"})

@login_required
@user_passes_test(_is_staff, login_url="login")
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect("event_detail", pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, "events/event_form.html", {"form": form, "action": "Edit", "event": event})

def error_404(request, exception=None):
    return render(request, "events/404.html", status=404)

def error_500(request):
    return render(request, "events/500.html", status=500)