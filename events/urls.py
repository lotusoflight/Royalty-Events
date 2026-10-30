"""Royalty Events — Application URL Configuration"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Public pages ──────────────────────────────────
    path("", views.home, name="home"),
    path("the-venue/", views.the_venue, name="the_venue"),
    path("weddings/", views.weddings, name="weddings"),
    path("celebrations/", views.celebrations, name="celebrations"),
    path("gallery/", views.gallery, name="gallery"),
    path("tour-our-venue/", views.tour_venue, name="tour_venue"),

    # ── Tour Enquiry ──────────────────────────────────
    path("book-a-tour/", views.book_tour, name="book_tour"),
    path("book-a-tour/success/<str:reference>/", views.book_tour_success, name="book_tour_success"),

    # ── Events — Public ───────────────────────────────
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/book/", views.book_event, name="book_event"),

    # ── API - ALL EVENTS (25 events) ──────────────────
    path("api/all-events/", views.all_events_api, name="all-events-api"),

    # ── Bookings (authenticated users) ───────────────
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),

    # ── Authentication ────────────────────────────────
    path("register/", views.register, name="register"),
    path("logout/", views.user_logout, name="logout"),

    # ── Staff Dashboard ───────────────────────────────
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/enquiries/", views.staff_enquiries, name="staff_enquiries"),
    path("dashboard/enquiries/<int:pk>/", views.enquiry_detail, name="enquiry_detail"),
]