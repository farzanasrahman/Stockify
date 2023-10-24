from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    User profile model representing additional details of a user.

    Attributes:
        user (User): One-to-one relation with Django's User model.
        phone_number (str): Phone number of the user.
        address (str): Address of the user.
        bio (str, optional): Short biography or description of the user.
        image (ImageField): Profile image of the user.
        balance (int): Financial balance associated with the user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    bio = models.TextField(null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    balance = models.IntegerField(default=0)

    def __str__(self):
        """
        String representation of the model instance.

        Returns:
            str: Username followed by 'Profile'.
        """
        return f'{self.user.username} Profile'

    def adjust_balance(self, balance, action):
        """
        Adjust the balance of the user.

        Args:
            balance (int): Amount by which to adjust the balance.
            action (str): Specifies the type of adjustment ('increment' or 'decrement').

        Returns:
            None
        """
        if action == 'increment':
            self.balance += balance
        else:
            self.balance -= balance

        self.save()
