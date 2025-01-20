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
    # path('owner-book-amenity', views.owner_book_amenity),
    # path('owner-maintenance', views.owner_maintenance),
    # path('owner-raise-complaint', views.owner_raise_complaint),
    # path('makepayment/<amount_to_pay>',views.makepayment),
    # path('paymentsuccess',views.paymentsuccess),



    path('admin-login', views.admin_login),
    path('admin-dashboard', views.admin_dashboard),
    path('admin-addnotice', views.admin_add_notice),
    path('admin-delete-notice/<nid>', views.admin_delete_notice),
    path('admin-usermanage', views.admin_usermanage),
    path('admin-add-amenity', views.admin_add_amenity),
    path('admin-view-amenity', views.admin_view_amenity),
    path('admin-delete-amenity/<aid>', views.admin_delete_amenity),
    path('admin-viewnotice', views.admin_view_notice),
    path('admin-add-poll', views.admin_add_poll),
    
    

]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)