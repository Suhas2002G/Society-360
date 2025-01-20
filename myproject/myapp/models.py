from django.db import models
from django.contrib.auth.models import User


#`````````      USER MODEL    ````````````

# Flat details Model
class Flat(models.Model):
    uid=models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    flat_no = models.CharField(max_length=10, null=True, blank=True)


# # Maintenance Payment Model
# class MaintenancePayment(models.Model):
#     uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
#     month = models.DateField()  # The month the payment corresponds to
#     payment_date = models.DateField()  # The actual payment date
#     amount= models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid
#     penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Penalty applied, if any


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
    question = models.CharField(max_length=200)
    option_1 = models.CharField(max_length=100)
    option_2 = models.CharField(max_length=100)
    votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.question


# # Poll Option Model
# class PollOption(models.Model):
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
#     option_text = models.CharField(max_length=100)
#     votes = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return f"{self.poll.question} - {self.option_text}"