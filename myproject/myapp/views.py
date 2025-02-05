from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.contrib.auth.models import User        
from django.contrib.auth import authenticate       
from django.contrib.auth import login,logout
from myapp.models import Notice, Flat, Amenity, MaintenancePayment, BookingAmenity, Complaint
from django.utils import timezone
from django.db.models import Q  
from datetime import date
import os
import datetime
import random
import razorpay
from django.core.mail import send_mail 
from datetime import datetime
from django.contrib.auth.decorators import login_required


# index page
def home(request):
    return render(request,'home.html')


# New User Registration
def owner_register(request):
    context={}
    if request.method == 'GET':
        return render(request,'owner-register.html')
    else:
        uname=request.POST['uname']
        ue=request.POST['uemail']
        p=request.POST['upass']
        cp=request.POST['ucpass']

        mob=request.POST['mob']
        flatno=request.POST['flatno']

        if uname=='' or ue=='' or p=='' or cp=='' or mob=='' or flatno=='':
            # print('Please fill all the fields')
            context['errormsg']='Please fill all the fields'
        elif len(p)<8:
            # print('Password must be atleast 8 character')
            context['errormsg']='Password must be atleast 8 character'
        elif p!=cp:
            context['errormsg']='Password and Confirm password must be same'
        # check whether entered flat no is already present or not in table
        elif Flat.objects.filter(flat_no=flatno).exists():
            context['errormsg']="This Flat's Owner is already Registered "
        else:
            try:
                u=User.objects.create(username=ue,email=ue,first_name=uname)
                u.set_password(p)  # set_password : To convert password into encripted form
                u.save()
                f=Flat.objects.create(mobile=mob,flat_no=flatno,uid=u)
                f.save
                context['success']='User Created Successfully'
            except Exception:
                context['errormsg']='User Already Exists'

        return render(request,'owner-register.html',context)
    

# User Login
def owner_login(request):
    context={}
    if request.method == 'GET':
        return render(request,'owner-login.html')
    else:
        e=request.POST['ue']
        p=request.POST['upass']
        u=authenticate(username=e,password=p) # For Authentication Purpose
        if u is not None:
            login(request,u)        # Login Method
            return redirect('/owner-home')
        else:
            context['errormsg']='Invalid Credential'
            return render(request,'owner-login.html',context)


# User/Admin Logout
def owner_logout(request):
    logout(request)
    return redirect('/')










# Forget Password functionality
# Send OTP
# def send_otp(request, uemail):
#     context = {}
#     u = User.objects.get(email=uemail)
#     user_email = order.uid.email
    
#     # Generate a random 4-digit OTP
#     otp = str(random.randint(1000, 9999))

#     # Save OTP to the database
#     OTP.objects.create(
#         oid=order,
#         otp=otp,
#         email=customer_email,
#     )
    
#     # Send OTP to customer email
#     send_mail(
#         'Your Order OTP',
#         f'Your OTP for order is {otp}. Kindly share it at the time of delivery.',
#         'santa.treasure2024@gmail.com',
#         [customer_email],
#         fail_silently=False,
#     )
#     return redirect('verify_otp', order_id=order.id)


# # OTP verification 
# def verify_otp(request, order_id):
#     context = {}
#     if request.method == 'POST':
#         input_otp = request.POST['otp']
#         try:
#             # otp_entry = OTP.objects.get(oid=order_id)
#             otp_entry = OTP.objects.filter(oid=order_id).order_by('-created_at').first()


#             # Check if the OTP is correct
#             if input_otp == otp_entry.otp:
#                 # Update the order status to "Delivered"
#                 order = otp_entry.oid  # Fetch the actual order object here
#                 order.status = 'Delivered'
#                 order.save()

#                 context['success_message'] = 'Order delivered successfully!'
#                 context['redirect'] = True  # Flag to trigger JavaScript redirect
#             else:
#                 context['error_message'] = 'Incorrect OTP. Please try again.'
        
#         except OTP.DoesNotExist:
#             return redirect('/trackorder')  # Or any appropriate redirect
    
#     # Pass the order_id and any messages to the template
#     return render(request, 'verify_otp.html', {'order_id': order_id, **context})













# Owner Home Page
@login_required(login_url='/owner-login')
def owner_home(request):
    context={}
    return render(request, 'owner-home.html', context)



# Notice Board for Owner
@login_required(login_url='/owner-login')
def owner_notice(request):
    context={}
    notices = Notice.objects.all().order_by('-created_at')
    context['notices'] = notices
    return render(request, 'owner-notice.html', context)





# Owner Maintenance Payment
@login_required(login_url='/owner-login')
def owner_maintenance(request):
    context = {}
    user = request.user  # Get the current logged-in user
    context['user'] = user

    # Get the current month (using year and month for comparison)
    current_month = timezone.now().date().replace(day=1)
    current_month_str = current_month.strftime('%Y-%m')  # Get year-month in 'YYYY-MM' format

    # Check if the user has already paid for the current month
    payment_exists = MaintenancePayment.objects.filter(uid=user, payment_date__month=current_month.month, payment_date__year=current_month.year).exists()

    if payment_exists:
        context['already_paid'] = "You have already paid your maintenance for this month."
        context['payment_status'] = 'paid'  # To disable Pay Now button in the template
    else:
        context['amount'] = 1000  # Amount to be paid

    # Fetch previous payment history (optional)
    previous_payments = MaintenancePayment.objects.filter(uid=user).order_by('-payment_date')
    context['previous_payments'] = previous_payments

    return render(request, 'owner-maintenance.html', context)




# Owner Make Payment Page
@login_required(login_url='/owner-login')
def makepayment(request):
    context={}
    RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
    RAZORPAY_API_PASS = os.getenv('RAZORPAY_API_PASS')

    # print(RAZORPAY_API_KEY)
    # print(RAZORPAY_API_PASS)

    amt = 1000
    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_PASS))

    amt = int(float(amt) * 100) # to convert amount to paise 

    data = { "amount": amt, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context['payment']=payment
    
    return render(request, 'pay.html', context)
    



# # Payment-Success page after paying Maintenance & Email Integration
@login_required(login_url='/owner-login')
def paymentsuccess(request):
    sub='Society360 Monthly Maintenance'
    msg="We have received monthly maintenance from your side. Thank you..! "
    frm=os.getenv('EMAIL_HOST_USER')

    u=User.objects.filter(id=request.user.id)    #email should go to authenticated user only 
    to=u[0].email
    print(u)            #<QuerySet [<User: suhas8838@gmail.com>]>
    print(u[0].email)   #suhas8838@gmail.com

    fid = Flat.objects.get(uid=request.user.id)
    # print(fid)

# send_mail() function should have following sequence of parameters
    send_mail(
        sub,
        msg,
        frm,
        [to],          #list beacause we can send mail to multiple emails-ids
        fail_silently=False  
        # if there is invalid email, then it will shows mail could not be delivered
    )

    # Insert a record in the MaintenancePayment model
    payment_data = {
        'uid': request.user,  
        'fid' : fid,
        'payment_date': timezone.now().date(),  
        'amount': 1000,  
    }
    
    # save the MaintenancePayment record
    MaintenancePayment.objects.create(**payment_data)

    return render(request, 'paymentsuccess.html')




# Owner View Book Amenity
@login_required(login_url='/owner-login')
def owner_book_amenity(request):
    context={}
    try:
        amenities = Amenity.objects.all()  # Fetching all amenities
        context['amenities'] = amenities
    except Exception :
        context['errormsg'] = "No Amenities Found "

    return render(request, 'owner-bookamenity.html', context)



# Owner Booking Amenity
@login_required(login_url='/owner-login')
def bookAmenity(request, aid):
    if request.method == 'GET':
        b_date = request.GET.get('booking_date')  # Get the booking date from query parameters
        context = {}

        # Check if the amenity is already booked on the given date
        existing_booking = BookingAmenity.objects.filter(aid=aid, booking_date=b_date).exists()

        if existing_booking:
            context['errormsg'] = "Amenity is booked by someone for the selected date."
            return render(request, 'owner-bookamenity.html', context)
        else:
            # Proceed with booking if not already booked
            a = Amenity.objects.get(id=aid)
            amount = a.rent

            RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
            RAZORPAY_API_PASS = os.getenv('RAZORPAY_API_PASS')

            amt = int(float(amount) * 100)  # Convert to paise
            client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_PASS))

            # Create payment order
            data = {"amount": amt, "currency": "INR", "receipt": f"order_rcptid_{aid}"}
            payment = client.order.create(data=data)
            context['payment'] = payment

            # Insert a record into the BookingAmenity model
            booking_data = {
                'uid': request.user,
                'booking_date': b_date,
                'payment_date': timezone.now().date(),
                'amount': amount,
                'aid': a,
            }

            BookingAmenity.objects.create(**booking_data)

            context['success_message'] = "Amenity booked successfully!"
            return render(request, 'amenitypay.html', context)

    return HttpResponse("Invalid request method.", status=405)



# Owner Amenity Payment Page
@login_required(login_url='/owner-login')
def amenitypaymentsuccess(request):
    sub='Society360 Amenity Booking Confirmation'
    msg="We have received your booking for amenity from your side. Thank you..! "
    frm=os.getenv('EMAIL_HOST_USER')

    u=User.objects.filter(id=request.user.id)       #email should go to authenticated user only 
    to=u[0].email

    send_mail(
        sub,
        msg,
        frm,
        [to],               #list beacause we can send mail to multiple emails-ids
        fail_silently=False
    )

    return render(request, 'paymentsuccess.html')


# View History of Bookings.
@login_required(login_url='/owner-login')
def owner_view_booking(request):
    a = BookingAmenity.objects.filter(uid = request.user.id)
    context={}
    context['data']=a
    return render(request, 'owner-view-booking.html', context)



def cancelbooking(request,id):
    context={}
    a = BookingAmenity.objects.filter(uid = request.user.id, id=id)
    # print(a)
    a.delete()
    return redirect('/owner-view-booking')


# Owner View Complaint
@login_required(login_url='/owner-login')
def owner_view_complaint(request):
    context={}
    c = Complaint.objects.filter(uid=request.user.id)
    print(c)
    context['data']=c 
    return render(request, 'owner-view-complaint.html', context)





# Owner can Raise Complaint
@login_required(login_url='/owner-login')
def owner_raise_complaint(request):
    context={}
    if request.method == 'GET':
        return render(request, 'owner-raise-complaint.html')
    else:
        t=request.POST['title']
        cat=request.POST.get('category')  # MultiValueDictKeyError
        desc=request.POST['description']

        print(t)
        print(cat)
        print(desc)
        u = request.user

        if t=='' or cat=='' or desc=='' :
            print('Please fill all the fields')
            context['errormsg']='Please fill all the fields'
        else:
            try:
                m=Complaint.objects.create(title=t,category=cat,description=desc,uid=u)
                m.save()
                context['success']='Complaint Raised Successfully...!'
            except Exception:
                context['errormsg']='Re-try Again'
        return render(request,'owner-raise-complaint.html',context)




# Emergency Contact List
@login_required(login_url='/owner-login')
def owner_emerg_contact(request):
    context={}
    return render(request, 'owner-emerg-contact.html', context)













#````````````````````````````````````````````````````````````
#~~~~~~~~~~~~~~~~~~~~~  ADMIN PART  ~~~~~~~~~~~~~~~~~~~~~~~~#
#............................................................





# Admin Login
def admin_login(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'admin-login.html', context)
    
    e = request.POST.get('ue')  # retrieve username
    p = request.POST.get('upass')  # retrieve password
    
    user = authenticate(username=e, password=p)  # Authenticate user
    if user:
        if user.is_staff:  # Check for staff privileges
            login(request, user)
            return redirect('/admin-dashboard')  # Redirect to admin dashboard
        context['errormsg'] = "You don't have Admin access"
    else:
        context['errormsg'] = 'Invalid Admin Credentials'
    return render(request, 'admin-login.html', context)  # Render the login page with error message



# Admin Dashboard
@login_required(login_url='/admin-login')
def admin_dashboard(request):
    context={}
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    else:
        current_datetime = timezone.now()  # Get current date (date and time)
        current_date = current_datetime.date()  # Get only the current date (without time)

        ownerCount=Flat.objects.count()
        noticeCount = Notice.objects.count()
        compCount = Complaint.objects.count()

        mamount = 0
        m=MaintenancePayment.objects.all()
        for i in m:
            mamount += i.amount
        
        context={
            'ocount': ownerCount,
            'ncount' : noticeCount,
            'current_date' : current_date,
            'mamount' : mamount,
            'compCount':compCount,
        }
        return render(request, 'admin-dashboard.html', context)



# Admin View Notice
@login_required(login_url='/admin-login')
def admin_view_notice(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    try:
        # Fetching all notices
        notices = Notice.objects.all().order_by('-created_at')
        context['notices'] = notices
    except Exception as e:
        context['errormsg'] = f"Error fetching notices: {e}"

    return render(request, 'admin-viewnotice.html', context)




# Admin can delete particular Notice
@login_required(login_url='/admin-login')
def admin_delete_notice(request,nid):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    notice = Notice.objects.filter(id=nid)
    # print(notice)
    # return HttpResponse('fetched')
    notice.delete()
    return redirect('/admin-viewnotice')



# Admin can edit particular Notice
@login_required(login_url='/admin-login')
def admin_edit_notice(request,nid):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    notice = Notice.objects.filter(id=nid)
    context['notices'] = notice
    return render(request, 'admin-edit-notice.html', context)


# Admin Add New Notice
@login_required(login_url='/admin-login')
def admin_add_notice(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    if request.method == 'GET':
        return render(request, 'admin-addnotice.html', context)
    else:
        title = request.POST['title']
        cat = request.POST.get('category')  # MultiValueDictKeyError
        des = request.POST['description']
        priority = request.POST.get('category')

        print(title)
        print(cat)
        print(des)
        print(priority)

        if not title or not cat or not des or not priority:
            context['errormsg'] = 'Please fill all the fields'
        else:
            try:
                Notice.objects.create(title=title, category=cat, des=des, priority=priority)
                context['successmsg'] = 'Notice has been successfully posted..!'
            except Exception:
                context['errormsg'] = 'An error occurred. Please try again later.'
        return render(request, 'admin-addnotice.html', context)



# Admin can do Owner Management
@login_required(login_url='/admin-login')
def admin_usermanage(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    users = User.objects.filter(is_staff=False) # Fetching users who are not staff (regular users)
    print(users)
    # Fetching flat details associated with users
    users_flats = []
    for user in users:
        try:
            flat = Flat.objects.get(uid=user.id)  # Using 'user' for ForeignKey relation
            users_flats.append({'user': user, 'flat': flat})
        except Flat.DoesNotExist:
            users_flats.append({'user': user, 'flat': None})
    
    context['users_flats'] = users_flats
    return render(request, 'admin-usermanage.html', context)


# Admin Maintenance Management
@login_required(login_url='/admin-login')
def admin_maintenance(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    m = MaintenancePayment.objects.all().order_by('-payment_date')
    context['data'] = m
    return render(request, 'admin-maintenance.html', context)



# Admin Maintenance Dashboard Filter
@login_required(login_url='/admin-login')
def admin_maintenance_filter(request):
    if not request.user.is_staff:  # Ensure only admins can access
        return redirect('/admin-login')

    context={}
    m = MaintenancePayment.objects.all()

    flatno = request.POST['flatno']  
    ownername = request.POST['oname']  
    start_date = request.POST['start_date'] 
    end_date = request.POST['end_date']  

    if flatno:
        m = m.filter(fid__flat_no__icontains=flatno)

    if ownername:
        m = m.filter(uid__first_name__icontains=ownername)

    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')  # Ensure the start date is converted to a datetime object
        m = m.filter(payment_date__gte=start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')  # Ensure the end date is converted to a datetime object
        # Set the time to the last moment of the end date (23:59:59.999999)
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        m = m.filter(payment_date__lte=end_date_obj)

    # Pass filtered results to the template
    context['data']=m
    return render(request, 'admin-maintenance.html', context)





# Admin Add New Amenity
@login_required(login_url='/admin-login')
def admin_add_amenity(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    if request.method == 'POST':
        # Fetching data from the form
        amenity_name = request.POST.get('amenity')
        description = request.POST.get('description')
        rent = request.POST.get('rent')
        img = request.FILES.get('img')

        # Validation
        if not amenity_name or not description or not rent or not img:
            context['errormsg'] = "Please fill in all the fields."
        else:
            try:
                # Saving the new amenity
                amenity = Amenity.objects.create(
                    amenity=amenity_name, 
                    des=description, 
                    rent=rent, 
                    img=img
                )
                amenity.save()
                context['successmsg'] = "Amenity added successfully!"
            except Exception as e:
                context['errormsg'] = f"Error adding amenity: {e}"

    return render(request, 'admin-addAmenity.html', context)



# Admin View Amenity
@login_required(login_url='/admin-login')
def admin_view_amenity(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    try:
        amenities = Amenity.objects.all()  # Fetching all amenities
        context['amenities'] = amenities
    except Exception as e:
        context['errormsg'] = f"Error fetching amenities: {e}"

    return render(request, 'admin-viewAmenity.html', context)




# Delete particular Amenity
@login_required(login_url='/admin-login')
def admin_delete_amenity(request,aid):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    amenity = Amenity.objects.filter(id=aid)
    amenity.delete()
    return redirect('/admin-view-amenity')






# Admin can see all bookings
@login_required(login_url='/admin-login')
def admin_booking(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    b = BookingAmenity.objects.all()
    context['data']=b
    return render(request, 'admin-booking-page.html', context)



# Complaint Lists
@login_required(login_url='/admin-login')
def admin_manage_complaint(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    c = Complaint.objects.all().order_by('-created_at')
    context['data']=c 
    return render(request, 'admin-manage-complaint.html', context)