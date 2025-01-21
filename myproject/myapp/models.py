from django.db import models
from django.contrib.auth.models import User


#`````````      USER MODEL    ````````````

# Flat details Model
class Flat(models.Model):
    uid=models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    flat_no = models.CharField(max_length=10, null=True, blank=True)


# Maintenance Payment Model
class MaintenancePayment(models.Model):
    uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    payment_date = models.DateField()  
    amount= models.DecimalField(max_digits=10, decimal_places=2)  
    

# Booking Amenity Model
class BookingAmenity(models.Model):
    uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    aid = models.ForeignKey('Amenity', on_delete=models.CASCADE, db_column='aid')
    booking_date = models.DateField()  
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()



# class ComplaintFeedback(models.Model):
#     CATEGORY_CHOICES = [
#         ('plumbing', 'Plumbing'),
#         ('security', 'Security'),
#         ('cleanliness', 'Cleanliness'),
#     ]
#     uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
#     description = models.TextField()
#     status = models.CharField(max_length=20, default='Pending')  # Pending, In Progress, Resolved
#     created_at = models.DateTimeField(auto_now_add=True)



#`````````      ADMIN MODEL    ````````````


# Notice Model
class Notice(models.Model):
    CAT = [
        ('events', 'Events'),
        ('maintenance', 'Maintenance Updates'),
        ('general', 'General Announcements'),
    ]
    title = models.CharField(max_length=100)
    des = models.TextField( db_column='description')
    category = models.CharField(max_length=20, choices=CAT)
    priority = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title



# Amenity Model [add]
class Amenity(models.Model):
    amenity = models.CharField(max_length=100)
    des = models.TextField(db_column='description')
    rent = models.IntegerField()
    img = models.ImageField(upload_to='image')


# Poll Model
class Poll(models.Model):
    question = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    votes_1 = models.IntegerField(default=0)
    votes_2 = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.question


