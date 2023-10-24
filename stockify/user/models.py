from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length =15)
    address = models.TextField()
    bio = models.TextField(null =True)
    image = models.ImageField(default='default.jpg',upload_to='profile_pics')
    balance = models.IntegerField(default=0)



    def __str__(self):
        return f'{self.user.username} Profile'
    
    def adjust_balance(self,balance,action):
        if action == 'increment':
            self.balance += balance
        else:
            self.balance -= balance

        self.save()

    

    


