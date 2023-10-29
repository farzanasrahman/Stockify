
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import StockList, StockDeposit
from unittest.mock import patch
from django.contrib.messages import get_messages



class BuyStockViewTest(TestCase):
    
    def setUp(self):
        # Create a user and user profile
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile = self.user.profile  # Assuming a profile is auto-created with user creation
        self.profile.phone_number = '1234567890'
        self.profile.address = 'Test Address'
        self.profile.balance = 10000
        self.profile.save()

        self.client = Client()

    def test_get_buy_stock_page(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('buy-stock'))
        self.assertEqual(response.status_code, 200)

    def test_buy_stock_sufficient_balance(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('buy-stock'), {'stock_name': 'MSFT', 'amount': 5})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful purchase
        
        # Simplified: Just check if balance decreased, not the exact amount
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.balance < 10000)

    def test_buy_stock_insufficient_balance(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('buy-stock'), {'stock_name': 'MSFT', 'amount': 150000})  # Huge amount for test
        self.assertEqual(response.status_code, 302)  # Expecting a redirect due to insufficient balance
        
        # Simplified: Check that balance remains the same
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, 10000)




class StockFetchViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.stock_list_url = reverse('stock-list') 

        # Create a sample user and log them in
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        # Create a sample StockList entry
        StockList.objects.create(symbol="TEST")

    @patch('stock.views.utils.stock_fetch_api')
    def test_stock_fetch(self, mock_stock_fetch_api):
        # Mock the return value of stock_fetch_api utility function
        mock_stock_fetch_api.return_value = {'TEST': 'Sample Data'}

        response = self.client.get(self.stock_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST')  


class SellStockTest(TestCase):
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Assume the profile is auto-created once a user is made, accessing it this way:
        self.profile = self.user.profile
        self.profile.phone_number = '1234567890'
        self.profile.address = 'Test Address'
        self.profile.save()
        
        # Create a stock deposit for the user
        self.stock_deposit = StockDeposit.objects.create(user=self.user, stock_name="AAPL", amount=5, unit_price=150, total_price=750)
        
        # Set up the client and login the user
        self.client = Client()
        self.client.login(username='testuser', password='password123')
        
        self.sell_stock_url = reverse('sell-stock')

    def test_sell_stock(self):
        # Test selling the stock
        response = self.client.post(self.sell_stock_url, {'deposit_id': self.stock_deposit.id})
        
        # Check if the stock deposit was deleted
        with self.assertRaises(StockDeposit.DoesNotExist):
            StockDeposit.objects.get(id=self.stock_deposit.id)
        
        # Check if the balance was incremented
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.balance, self.stock_deposit.total_price)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully sold the stock!")
        
    def test_sell_other_users_stock(self):
        # Create another user and login
        other_user = User.objects.create_user(username='otheruser', password='password123')
        self.client.login(username='otheruser', password='password123')
        
        # Try to sell stock of the test user
        response = self.client.post(self.sell_stock_url, {'deposit_id': self.stock_deposit.id})
        
        # Check that the stock deposit wasn't deleted
        self.assertTrue(StockDeposit.objects.filter(id=self.stock_deposit.id).exists())
        
        # Check warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not allowed to sell this stock!")