from django.contrib import admin
from myapp.models import (
    Flat,
    MaintenancePayment,
    BookingAmenity,
    Complaint,
    Notice,
    Amenity,
    Refund,
)



# Flat model registration
class FlatAdmin(admin.ModelAdmin):
    list_display = ('uid', 'mobile', 'flat_no')
    search_fields = ('flat_no', 'mobile')
    list_filter = ('flat_no',)

# MaintenancePayment model registration
class MaintenancePaymentAdmin(admin.ModelAdmin):
    list_display = ('uid', 'fid', 'payment_date', 'amount')
    search_fields = ('uid__username', 'fid__flat_no')
    list_filter = ('payment_date',)

# BookingAmenity model registration
class BookingAmenityAdmin(admin.ModelAdmin):
    list_display = ('uid', 'aid', 'booking_date', 'amount', 'payment_date')
    search_fields = ('uid__username', 'aid__amenity')
    list_filter = ('booking_date',)

# Complaint model registration
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('uid', 'title', 'category', 'created_at')
    search_fields = ('title', 'category', 'uid__username')
    list_filter = ('category', 'created_at')

# Notice model registration
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'created_at', 'updated_at')
    search_fields = ('title', 'category')
    list_filter = ('category', 'priority')

# Amenity model registration
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('amenity', 'rent')
    search_fields = ('amenity',)
    list_filter = ('rent',)

# Refund model registration
class RefundAdmin(admin.ModelAdmin):
    list_display = ('uid', 'aid', 'amount', 'payment_date','status')
    search_fields = ('status','payment_date')
    list_filter = ('status','payment_date')


admin.site.register(Flat,FlatAdmin) 
admin.site.register(MaintenancePayment,MaintenancePaymentAdmin) 
admin.site.register(BookingAmenity,BookingAmenityAdmin) 
admin.site.register(Complaint,ComplaintAdmin) 
admin.site.register(Notice,NoticeAdmin) 
admin.site.register(Amenity,AmenityAdmin) 
admin.site.register(Refund,RefundAdmin) 