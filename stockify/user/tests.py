from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class ProfileTestCase(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Create a profile for the user
        self.profile = Profile.objects.create(user=self.user, phone_number='1234567890', address='Test Address')

    def test_profile_created(self):
        """Test if the profile is created for the user."""
        self.assertIsNotNone(self.profile)

    def test_profile_string_representation(self):
        """Test the string representation of the profile."""
        self.assertEqual(str(self.profile), 'testuser Profile')

    def test_adjust_balance_increment(self):
        """Test if the balance is correctly incremented."""
        initial_balance = self.profile.balance
        increment_value = 100
        self.profile.adjust_balance(increment_value, 'increment')
        self.assertEqual(self.profile.balance, initial_balance + increment_value)

    def test_adjust_balance_decrement(self):
        """Test if the balance is correctly decremented."""
        initial_balance = self.profile.balance
        decrement_value = 50
        self.profile.adjust_balance(decrement_value, 'decrement')
        self.assertEqual(self.profile.balance, initial_balance - decrement_value)

    def test_default_image(self):
        """Test if default image is set for profile."""
        self.assertEqual(self.profile.image.name, 'default.jpg')
