from django.urls import path
from myapp import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home),
    path('owner-login', views.owner_login),
    path('owner-register', views.owner_register),
    path('logout', views.owner_logout),
    path('forgetpass', views.forgetpass),
    path('sendOTP', views.sendOTP),
    path('verify-otp', views.verify_otp),
    path('setPass', views.setPass),
    path('owner-home', views.owner_home),
    path('owner-notice', views.owner_notice),
    path('owner-book-amenity', views.owner_book_amenity),   # to view all amenity
    path('owner-view-booking', views.owner_view_booking),   # to view all bookings
    path('cancelbooking/<id>', views.cancelbooking),
    path('bookAmenity/<aid>', views.bookAmenity),    # to book particular amenity
    path('owner-maintenance', views.owner_maintenance),
    path('owner-view-complaint', views.owner_view_complaint),
    path('owner-raise-complaint', views.owner_raise_complaint),
    path('owner-emerg-contact', views.owner_emerg_contact),
    path('makepayment',views.makepayment),
    path('paymentsuccess',views.paymentsuccess),
    path('amenitypaymentsuccess',views.amenitypaymentsuccess),

    path('admin-login', views.admin_login),
    path('admin-dashboard', views.admin_dashboard),
    path('admin-addnotice', views.admin_add_notice),
    path('admin-delete-notice/<nid>', views.admin_delete_notice),
    path('admin-usermanage', views.admin_usermanage),
    path('removeOwner/<id>', views.removeOwner),
    path('admin-maintenance', views.admin_maintenance),
    path('admin-maintenance-filter', views.admin_maintenance_filter),
    path('admin-add-amenity', views.admin_add_amenity),
    path('admin-view-amenity', views.admin_view_amenity),
    path('admin-delete-amenity/<aid>', views.admin_delete_amenity),
    path('admin-edit-amenity/<aid>', views.admin_edit_amenity),
    path('admin-viewnotice', views.admin_view_notice),
    path('admin-booking', views.admin_booking),
    path('admin-manage-complaint', views.admin_manage_complaint),
    path('refund', views.refund),
    path('changeStatus/<id>', views.changeStatus),
    path('admin-maintenance-download', views.download_maintenance_excel, name='admin-maintenance-download'),
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)