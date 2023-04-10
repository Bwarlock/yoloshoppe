from django.db import models
from django.contrib.auth.models import User

class CartModel(models.Model):
    user = models.ForeignKey(User , related_name='cartmodel' , on_delete=models.CASCADE)
    key = models.IntegerField(null=True)
    value = models.IntegerField(null=True)
    def __str__(self):
        return self.user.username

