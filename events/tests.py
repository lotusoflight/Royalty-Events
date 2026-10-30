from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from events.models import Booking, Category, Event, TourEnquiry
from events.forms import TourEnquiryForm, BookingForm, RegisterForm


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testclient", email="client@royalty.com", password="password123"
        )
        self.category = Category.objects.create(name="Gala", description="Grand galas")
        self.event = Event.objects.create(
            title="Royal Autumn Gala",
            description="An exquisite gala evening.",
            event_date=timezone.now() + timedelta(days=14),
            location="The Grand Ballroom",
            total_seats=50,
            price=2500.00,
            category=self.category,
            created_by=self.user,
            is_published=True,
        )

    def test_category_creation_and_str(self):
        self.assertEqual(str(self.category), "Gala")

    def test_event_available_seats_and_is_full(self):
        self.assertEqual(self.event.available_seats, 50)
        self.assertFalse(self.event.is_full)
        self.assertTrue(self.event.is_upcoming)

        # Create a confirmed booking for 50 seats
        Booking.objects.create(
            user=self.user,
            event=self.event,
            seats=50,
            status="confirmed",
        )
        self.assertEqual(self.event.available_seats, 0)
        self.assertTrue(self.event.is_full)

    def test_booking_reference_and_total_price(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            seats=2,
            status="confirmed",
        )
        self.assertTrue(booking.reference.startswith("BK"))
        self.assertEqual(booking.total_price, 5000.00)

    def test_cancelled_booking_frees_seats(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            seats=10,
            status="confirmed",
        )
        self.assertEqual(self.event.available_seats, 40)
        booking.status = "cancelled"
        booking.save()
        self.assertEqual(self.event.available_seats, 50)

    def test_tour_enquiry_creation_and_reference(self):
        future_date = (timezone.now() + timedelta(days=30)).date()
        enquiry = TourEnquiry.objects.create(
            full_name="Lady Catherine",
            email="catherine@estate.co.uk",
            phone="+1 555-019-2834",
            event_type="Wedding + Reception",
            event_date=future_date,
            guest_count=150,
            status="new",
        )
        self.assertTrue(enquiry.reference.startswith("TQ"))
        self.assertEqual(str(enquiry), f"{enquiry.reference} — Lady Catherine (Wedding + Reception)")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="regularuser", email="user@test.com", password="password123"
        )
        self.staff_user = User.objects.create_user(
            username="staffmember", email="staff@test.com", password="password123", is_staff=True
        )
        self.category = Category.objects.create(name="Corporate", description="Conferences")
        self.event = Event.objects.create(
            title="Tech Summit 2026",
            description="Annual executive summit",
            event_date=timezone.now() + timedelta(days=7),
            location="Skyline Terrace",
            total_seats=20,
            price=1500.00,
            category=self.category,
            created_by=self.staff_user,
            is_published=True,
        )

    def test_public_pages_load_successfully(self):
        pages = [
            reverse("home"),
            reverse("the_venue"),
            reverse("weddings"),
            reverse("celebrations"),
            reverse("gallery"),
            reverse("tour_venue"),
            reverse("event_list"),
            reverse("event_detail", kwargs={"pk": self.event.pk}),
            reverse("book_tour"),
            reverse("register"),
        ]
        for url in pages:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                200,
                f"URL {url} failed to load with status {response.status_code}",
            )

    def test_book_tour_post_persists_enquiry_and_redirects(self):
        future_date = (timezone.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        post_data = {
            "full_name": "Eleanor Vance",
            "email": "eleanor@vance.com",
            "phone": "+1 713-555-0199",
            "event_type": "Birthday Celebration",
            "event_date": future_date,
            "guest_count": 80,
            "experience": "Venue Rental",
            "investment_range": "$5000-$7,500",
            "vision": "Looking forward to seeing the chandeliers.",
        }
        response = self.client.post(reverse("book_tour"), data=post_data)
        self.assertEqual(response.status_code, 302)

        enquiry = TourEnquiry.objects.filter(email="eleanor@vance.com").first()
        self.assertIsNotNone(enquiry)
        self.assertEqual(enquiry.full_name, "Eleanor Vance")
        self.assertRedirects(response, reverse("book_tour_success", kwargs={"reference": enquiry.reference}))

    def test_booking_event_requires_login(self):
        response = self.client.post(
            reverse("book_event", kwargs={"pk": self.event.pk}),
            data={"seats": 2},
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_booking_event_authenticated_flow(self):
        self.client.login(username="regularuser", password="password123")
        response = self.client.post(
            reverse("book_event", kwargs={"pk": self.event.pk}),
            data={"seats": 3},
        )
        self.assertRedirects(response, reverse("my_bookings"))
        self.assertEqual(Booking.objects.filter(user=self.user, event=self.event).count(), 1)
        booking = Booking.objects.get(user=self.user, event=self.event)
        self.assertEqual(booking.seats, 3)
        self.assertEqual(self.event.available_seats, 17)

    def test_prevent_overbooking(self):
        self.client.login(username="regularuser", password="password123")
        # Attempt to book 25 seats when only 20 are available
        response = self.client.post(
            reverse("book_event", kwargs={"pk": self.event.pk}),
            data={"seats": 25},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.filter(user=self.user, event=self.event).count(), 0)

    def test_staff_dashboard_access_control(self):
        # Anonymous user denied
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

        # Regular user denied
        self.client.login(username="regularuser", password="password123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

        # Staff user allowed
        self.client.login(username="staffmember", password="password123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_home(self):
        self.client.login(username="regularuser", password="password123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
