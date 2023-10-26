from django.db import models
from django.contrib.auth.models import User


class StockDeposit(models.Model):
    """
    Represents the stock deposit of a user.

    Attributes:
    - user: The User associated with the stock deposit.
    - stock_name: The name of the stock.
    - amount: The quantity of the stock.
    - unit_price: The price of a single stock unit.
    - total_price: The total price for the amount of stock.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=100)
    amount = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Returns a string representation of the stock deposit."""
        return f'{self.user.username} - {self.stock_name}'


class StockList(models.Model):
    """
    Represents a stock in the list.

    Attributes:
    - name: The name of the stock.
    - symbol: The stock's symbol.
    """

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        """Returns a string representation of the stock."""
        return f'{self.name} - {self.symbol}'

