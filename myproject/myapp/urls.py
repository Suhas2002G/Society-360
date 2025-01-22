from django.urls import path
from myapp import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home),
    path('owner-login', views.owner_login),
    path('owner-register', views.owner_register),
    path('logout', views.owner_logout),
    path('owner-home', views.owner_home),
    path('owner-notice', views.owner_notice),
    path('owner-view-poll', views.owner_view_poll),
    path('vote/<vid>/<op>', views.vote),
    path('owner-book-amenity', views.owner_book_amenity),   # to view all amenity
    path('bookAmenity/<aid>', views.bookAmenity),    # to book particular amenity
    path('owner-maintenance', views.owner_maintenance),
    path('owner-raise-complaint', views.owner_raise_complaint),
    path('makepayment',views.makepayment),
    path('paymentsuccess',views.paymentsuccess),
    path('amenitypaymentsuccess',views.amenitypaymentsuccess),



    path('admin-login', views.admin_login),
    path('admin-dashboard', views.admin_dashboard),
    path('admin-addnotice', views.admin_add_notice),
    path('admin-delete-notice/<nid>', views.admin_delete_notice),
    path('admin-edit-notice/<nid>', views.admin_edit_notice),
    path('admin-usermanage', views.admin_usermanage),
    path('admin-maintenance', views.admin_maintenance),
    path('admin-add-amenity', views.admin_add_amenity),
    path('admin-view-amenity', views.admin_view_amenity),
    path('admin-delete-amenity/<aid>', views.admin_delete_amenity),
    path('admin-delete-poll/<pid>', views.admin_delete_poll),
    path('admin-viewnotice', views.admin_view_notice),
    path('admin-add-poll', views.admin_add_poll),
    path('admin-view-poll', views.admin_view_poll),
    path('admin-booking', views.admin_booking),
    path('admin-manage-complaint', views.admin_manage_complaint),
    
    

]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)