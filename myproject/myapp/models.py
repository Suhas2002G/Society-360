from django.db import models
from django.contrib.auth.models import User


#`````````      USER MODEL    ````````````

# Flat details Model
class Flat(models.Model):
    uid=models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='uid')
    mobile = models.CharField(max_length=10, unique=True, null=True, blank=True, help_text='Mobile number should be 10 digit')
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

    def __str__(self):
        return self.title


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

    def __str__(self):
        return self.amenity




'''
That’s a solid start, Suhas 👍 — your Django `models.py` is **structured well** and shows a clear understanding of how to model real-world entities (users, flats, amenities, payments, etc.) in a society management system.

But there **are a few key improvements** and **relational adjustments** you can make to make it more robust, consistent, and in line with Django best practices.

Let’s review it **section by section** 👇

---

## 🧱 1. General Observations

✅ **Strengths**

* Relationships between users, flats, amenities, and payments are logically designed.
* Good use of `ForeignKey` with `on_delete=models.CASCADE` — this keeps data integrity intact.
* You’ve considered real-world flows: payments, refunds, complaints, OTPs — good modeling thinking.

⚠️ **Improvements**

* You’re using `'auth.user'` string references instead of the `User` model directly — that’s fine, but not ideal for flexibility.
* You should use `settings.AUTH_USER_MODEL` to future-proof the project.
* Naming conventions (`uid`, `aid`, `fid`) are short — but they can be more descriptive like `user`, `amenity`, `flat` for readability.
* Some models are missing `__str__` for admin readability.
* Some fields (e.g., `mobile`, `flat_no`) could use constraints or validation logic.
* There’s a **potential circular dependency** with `Amenity` being defined after `BookingAmenity` and `Refund`.

---

## 🧩 2. Relationship Review

### ✅ `Flat`

```python
class Flat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=10, unique=True, null=True, blank=True)
    flat_no = models.CharField(max_length=10, null=True, blank=True)
```

✅ Relationship: One user → can have many flats (makes sense).
⚠️ You might later need to consider a unique constraint per flat number or per building if the app supports multiple societies.

---

### ✅ `MaintenancePayment`

```python
class MaintenancePayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flat = models.ForeignKey('Flat', on_delete=models.CASCADE, null=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
```

✅ Logical — a user pays maintenance for a flat.
⚠️ Consider adding:

* `payment_id` for transaction tracking
* `status` field (Success / Pending / Failed)
* Add `__str__` method for admin visibility.

---

### ⚠️ `BookingAmenity`

```python
class BookingAmenity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amenity = models.ForeignKey('Amenity', on_delete=models.CASCADE)
    booking_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_id = models.CharField(max_length=50, default='xyz', null=True, blank=True)
```

✅ Relation makes sense — user books an amenity.
⚠️ Improvements:

* Add a `status` (Booked / Cancelled / Completed).
* Maybe a `start_time` / `end_time` if amenities are time-bound.
* Add `unique_together = ('user', 'amenity', 'booking_date')` to prevent duplicate bookings.

---

### ⚠️ `Refund`

```python
class Refund(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amenity = models.ForeignKey('Amenity', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_id = models.CharField(max_length=50, default='xyz', null=True, blank=True)
```

✅ Good addition for business logic.
⚠️ Better to link `Refund` to a `BookingAmenity` instead of `Amenity` directly:

```python
booking = models.ForeignKey('BookingAmenity', on_delete=models.CASCADE)
```

That way, you know **which booking** the refund belongs to.

---

### ✅ `Complaint`

✅ Logical and simple.
⚠️ Add `priority` and possibly `resolved_at` to track progress.
✅ You already added `status`, which is good.

---

### ✅ `Otp`

✅ Simple and functional.
⚠️ Add `is_verified` (BooleanField) and maybe expiry logic later.

---

### ⚠️ `Notice`

✅ Correct, but add a `created_by` (Admin user) field for audit purposes.
✅ Using `category` and `priority` is fine, though consider `choices` for consistent data.

---

### ✅ `Amenity`

✅ Looks fine.
⚠️ Add availability logic later (e.g., `is_active`, `max_bookings_per_day`).

---

## 🧩 3. Recommended Refactor (clean, consistent)

Here’s a **cleaner and more scalable** version of your model relationships:

```python
from django.db import models
from django.conf import settings

class Flat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=10, unique=True)
    flat_no = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.flat_no} - {self.user.username}"


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    rent = models.IntegerField()
    image = models.ImageField(upload_to='image')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MaintenancePayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(max_length=20, default='Paid')
    payment_id = models.CharField(max_length=50, blank=True, null=True)


class BookingAmenity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    booking_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default='Booked')


class Refund(models.Model):
    booking = models.ForeignKey(BookingAmenity, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending')
    created_at = models.DateField(auto_now_add=True)


class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    resolved_at = models.DateTimeField(null=True, blank=True)


class Notice(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    priority = models.CharField(max_length=20)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Otp(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=4)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🧠 Summary (Relationship Evaluation)

| Model                          | Relationship                          | Status                   | Suggestion |
| ------------------------------ | ------------------------------------- | ------------------------ | ---------- |
| Flat → User                    | ✅ Correct                             | Maybe use `related_name` |            |
| MaintenancePayment → Flat/User | ✅ Correct                             | Add status/payment_id    |            |
| BookingAmenity → Amenity/User  | ✅ Correct                             | Add status/time fields   |            |
| Refund → Amenity               | ⚠️ Should be linked to BookingAmenity |                          |            |
| Complaint → User               | ✅ Correct                             | Add resolved date        |            |
| Notice                         | ✅                                     | Add created_by           |            |
| Otp                            | ✅                                     | Add verified field       |            |

---

Would you like me to diagram these models (ER diagram-style) to visualize how they relate to each other? That would make it easier to confirm if the relationships match your project logic.
'''