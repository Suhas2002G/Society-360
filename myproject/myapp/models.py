from django.db import models
from django.contrib.auth.models import User


#`````````      USER MODEL    ````````````

# Flat details Model
class Flat(models.Model):
    uid=models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    mobile = models.CharField(max_length=10, unique=True, null=True, blank=True)
    flat_no = models.CharField(max_length=10, null=True, blank=True)


# Maintenance Payment Model
class MaintenancePayment(models.Model):
    uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    fid = models.ForeignKey('Flat', on_delete=models.CASCADE, db_column='fid', null=True)
    payment_date = models.DateField()  
    amount= models.DecimalField(max_digits=10, decimal_places=2)  
    

# Booking Amenity Model
class BookingAmenity(models.Model):
    uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    aid = models.ForeignKey('Amenity', on_delete=models.CASCADE, db_column='aid')
    booking_date = models.DateField()  
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_id = models.CharField(max_length=50, default='xyz', null=True, blank=True)



# for refund purpose [after amenity cancellationn]
class Refund(models.Model):
    uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    aid = models.ForeignKey('Amenity', on_delete=models.CASCADE, db_column='aid')  
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_id = models.CharField(max_length=50,  default='xyz', null=True, blank=True)


# Complaint Model
class Complaint(models.Model):
    uid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending', null=True, blank=True)


# To Otp while Forget Password 
class Otp(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=4)


#`````````      ADMIN MODEL    ````````````


# Notice Model
class Notice(models.Model):
    # CAT = [
    #     ('events', 'Events'),
    #     ('maintenance', 'Maintenance Updates'),
    #     ('general', 'General Announcements'),
    # ]
    title = models.CharField(max_length=100)
    des = models.TextField( db_column='description')
    category = models.CharField(max_length=20)  #choices=CAT
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


# OLD DEMO Amenity Model [add]
# class Amenity(models.Model):
#     amenity = models.CharField(max_length=100)
#     des = models.TextField(db_column='description')
#     rent = models.IntegerField()
#     img = models.ImageField(upload_to='image')


