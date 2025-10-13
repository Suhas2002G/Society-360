from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.contrib.auth.models import User        
from django.contrib.auth import authenticate       
from django.contrib.auth import login,logout
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from myapp.models import Notice, Flat, Amenity, MaintenancePayment, BookingAmenity, Complaint, Otp, Refund
from django.utils import timezone
from django.db.models import Q  
from datetime import date
import logging
import os
import datetime
import random
import razorpay
from django.core.mail import send_mail 
from datetime import datetime
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.db.models.functions import TruncMonth
from django.db.models import Sum

# Initialize logger for this module
logger = logging.getLogger(__name__)

# index page
def home(request):
    return render(request,'home.html')



#----------------------------------------
#       AUTHENTICATION
#----------------------------------------

def owner_register(request):
    """
    Handle registration of flat owners.

    HTTP requests:
    - GET: Render the registration form.
    - POST: Validate form input, create a User and associated Flat record.

    Returns:
        HttpResponse: Rendered registration page with success or error message.
    """
    context={}

    # If GET request, just render the registration form
    if request.method == 'GET':
        return render(request,'owner-register.html')
    
    # Extract POST data safely using `.get()` to avoid KeyError
    uname = request.POST.get('uname', '').strip()
    email = request.POST.get('uemail', '').strip()
    password = request.POST.get('upass', '').strip()
    confirm_password = request.POST.get('ucpass', '').strip()
    mobile = request.POST.get('mob', '').strip()
    flat_no = request.POST.get('flatno', '').strip()

    # Validate input fields
    if not all([uname, email, password, confirm_password, mobile, flat_no]):
        context['errormsg'] = 'Please fill all the fields.'
        return render(request, 'owner-register.html', context)

    if len(password) < 8:
        context['errormsg'] = 'Password must be at least 8 characters long.'
        return render(request, 'owner-register.html', context)

    if password != confirm_password:
        context['errormsg'] = 'Password and Confirm Password must match.'
        return render(request, 'owner-register.html', context)

    # Check if flat already registered
    if Flat.objects.filter(flat_no=flat_no).exists():
        logger.warning(f"This flat's owner is already registered")
        context['errormsg'] = "This flat's owner is already registered."
        return render(request, 'owner-register.html', context)

    # Attempt to create user and flat atomically
    try:
        # Used transaction.atomic() to ensure both user and flat are created together
        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=uname,
                password=password  # Django handles hashing automatically
            )
            Flat.objects.create(
                uid=user,
                mobile=mobile,
                flat_no=flat_no
            )

        context['success'] = 'User registered successfully.'
    
    except IntegrityError as e:
        logger.warning(f"IntegrityError during registration: {e}")
        context['errormsg'] = 'User with this email already exists.'

    except ValidationError as e:
        logger.error(f"ValidationError: {e.messages}")
        context['errormsg'] = f'Invalid data: {e.messages[0]}'

    except Exception as e:
        logger.exception("Unexpected error during owner registration")
        context['errormsg'] = 'Unexpected error occurred. Please try again later.'


    return render(request, 'owner-register.html', context)
    


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



def forgetpass(request):
    return render(request, 'forget-password.html')



def sendOTP(request):
    context = {}
    if request.method == "POST":
        e = request.POST.get("uemail")

        # Check if user exists
        if User.objects.filter(email=e).exists():
            otp = str(random.randint(1000, 9999))

            # Save OTP 
            Otp.objects.create(otp=otp, email=e)

            # Store email in session
            request.session['reset_email'] = e  

            # Send OTP to user email
            send_mail(
                'Reset Password',
                f"Your OTP for password reset is: {otp}",
                os.getenv('EMAIL_HOST_USER'),
                [e],
                fail_silently=False,
            )

            return redirect('/verify-otp')  # Redirect without email in URL
        else:
            context['errormsg'] = 'This email ID is not registered with us!'
            return render(request, 'forget-password.html', context)



def verify_otp(request):
    context = {}
    e = request.session.get('reset_email')   # Retrieve email from session
    if not e:
        return redirect('/forgetpass')  # Redirect if email is missing

    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        otp_entry = Otp.objects.filter(email=e).order_by('-created_at').first()
 
        if otp_entry.otp == input_otp:
            return redirect('/setPass')  # Redirect to password reset page
        else:
            context['error_message'] = 'Incorrect OTP. Please try again.'
    return render(request, 'verify-otp.html', context)




def setPass(request):
    context = {}
    e = request.session.get('reset_email')  # Retrieve email from session
    if not e:
        return redirect('/forgetpass')
    
    if request.method == 'GET':
        return render(request, 'setPass.html')
    else:
        p = request.POST.get('pass', '')
        cp = request.POST.get('cpass', '')

        if p=='' or cp=='':
            context['error_message'] = 'Please fill in all fields.'
        elif p != cp:
            context['error_message'] = 'Passwords do not match.'
        else:
            try:
                user = User.objects.filter(email=e).first()
                if user:
                    user.set_password(p)
                    user.save()
                    request.session.flush()  # Clear session data after successful reset
                    context['success_message'] = 'Password Successfully Reset.'
                    return render(request,'setPass.html', context)  # Redirect to login page
                    
                else:
                    context['error_message'] = 'User not found.'
            except Exception as err:
                context['error_message'] = 'An error occurred. Please try again.'

    return render(request, 'setPass.html', context)







# Owner Home Page
@login_required(login_url='/owner-login')
def owner_home(request):
    context={}
    notice = Notice.objects.order_by('-created_at')[:2]
    print(notice)

    context['notice']=notice

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

    print(RAZORPAY_API_KEY)
    print(RAZORPAY_API_PASS)

    amt = 1000
    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_PASS))

    amt = int(float(amt) * 100) # to convert amount to paise 

    data = { "amount": amt, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context['payment']=payment

    print(payment)

    context['RAZORPAY_API_KEY']=RAZORPAY_API_KEY
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




@login_required(login_url='/owner-login')
def bookAmenity(request, aid):
    if request.method == 'GET':
        b_date = request.GET.get('booking_date')  # Get the booking date from query parameters
        context = {}

        # Convert the booking date to a date object
        booking_date = timezone.datetime.strptime(b_date, '%Y-%m-%d').date()

        # Check if the selected booking date is in the future
        today = date.today()
        if booking_date < today:
            context['errormsg'] = "Please select a future date for booking."
            return render(request, 'owner-bookamenity.html', context)

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

            # print(RAZORPAY_API_KEY)
            # print(RAZORPAY_API_PASS)

            amt = int(float(amount) * 100)  # Convert to paise
            client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_PASS))

            # Create payment order
            data = {"amount": amt, "currency": "INR", "receipt": f"order_rcptid_{aid}"}
            payment = client.order.create(data=data)
            context['payment'] = payment
            print(payment)
            payment_id = payment['id']
            print(payment_id)
            context['RAZORPAY_API_KEY']=RAZORPAY_API_KEY

            # Insert a record into the BookingAmenity model
            booking_data = {
                'uid': request.user,
                'booking_date': b_date,
                'payment_date': timezone.now().date(),
                'amount': amount,
                'aid': a,
                'payment_id': payment_id
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
    a = BookingAmenity.objects.filter(uid = request.user.id).order_by('-booking_date')
    context={}
    context['data']=a
    return render(request, 'owner-view-booking.html', context)



def cancelbooking(request,id):
    context={}
    a = BookingAmenity.objects.filter(uid = request.user.id, id=id).first()
    print(a)

    # load record into refund table
    Refund.objects.create(
        uid=a.uid,
        aid=a.aid,
        amount=a.amount,  
        payment_date=a.payment_date,
        status='Pending',  #default pending
        payment_id = a.payment_id
    )

    a.delete()
    return redirect('/owner-view-booking')


# Owner View Complaint
@login_required(login_url='/owner-login')
def owner_view_complaint(request):
    context={}
    c = Complaint.objects.filter(uid=request.user.id).order_by('-created_at')
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

        # m=MaintenancePayment.objects.filter(payment_date__month=1) # get only Jan records
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

            # Aggregate maintenance payments by month
        monthly_payments = (
            MaintenancePayment.objects
            .annotate(month=TruncMonth('payment_date'))  # Extract month from payment_date
            .values('month')  # Group by month
            .annotate(total_amount=Sum('amount'))  # Sum amounts for each month
            .order_by('month')  # Order by month
        )

        # Convert QuerySet to lists for JavaScript
        months = [entry['month'].strftime('%b %Y') for entry in monthly_payments]  # Format: "Jan 2025"
        amounts = [float(entry['total_amount']) for entry in monthly_payments]

        context = {
            'ocount': ownerCount,
            'ncount': noticeCount,
            'current_date': current_date,
            'mamount' : mamount,
            'compCount': compCount,
            'months': months,  # Pass month labels to template
            'amounts': amounts,  # Pass corresponding amount data
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
        cat = request.POST.get('category')  
        des = request.POST['description']
        priority = 'None'

        if not title or not cat or not des or not priority:
            context['errormsg'] = 'Please fill all the fields'
        else:
            try:
                Notice.objects.create(title=title, category=cat, des=des, priority=priority)
                context['successmsg'] = 'Notice has been successfully posted..!'
 
                # Twilio SMS Integration
                account_sid = os.getenv('ACCOUNT_SID')
                auth_token = os.getenv('AUTH_TOKEN')
                client = Client(account_sid, auth_token)

                message = client.messages.create(
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                body='Admin Alert : A new notice has been added. Please check it at Society-360 portal for details.',
                to='+917755994279'
                )
                # print(message.sid)

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
    
    # Fetching flat details associated with users
    users_flats = []
    for user in users:
        try:
            flat = Flat.objects.get(uid=user.id)  # Using 'user' for ForeignKey relation
            users_flats.append({'user': user, 'flat': flat, 'uid':user.id})
        except Flat.DoesNotExist:
            users_flats.append({'user': user, 'flat': None})
    
    context['users_flats'] = users_flats
    return render(request, 'admin-usermanage.html', context)


# Admin can remove Owner 
@login_required(login_url='/admin-login')
def removeOwner(request,id):
    u = User.objects.filter(id=id)
    print(u)
    u.delete()
    return redirect('/admin-usermanage')



# Admin Maintenance Management
@login_required(login_url='/admin-login')
def admin_maintenance(request):
    '''Admin Maintenance Management'''
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



# Edit particular Amenity
@login_required(login_url='/admin-login')
def admin_edit_amenity(request, aid):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    try:
        amenity = Amenity.objects.get(id=aid)  # Fetch the amenity object
        
        if request.method == 'GET':
            context['data'] = [amenity]  
        
        elif request.method == 'POST':
            if 'amenity' in request.POST:
                amenity.amenity = request.POST.get('amenity')
            if 'description' in request.POST:
                amenity.description = request.POST.get('description')
            if 'rent' in request.POST:
                amenity.rent = request.POST.get('rent')

            # Handle image upload if it's provided
            if 'img' in request.FILES:
                amenity.img = request.FILES['img']
            
            amenity.save()  # Save the updated amenity

            context['successmsg'] = "Amenity updated successfully!"
            return render(request, 'admin-editAmenity.html', context)

    except Amenity.DoesNotExist:
        context['errormsg'] = "Amenity not found!"
        return render(request, 'admin-editAmenity.html', context)

    return render(request, 'admin-editAmenity.html', context)



# Admin can see all bookings
@login_required(login_url='/admin-login')
def admin_booking(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    b = BookingAmenity.objects.all().order_by('-booking_date')
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




# Refund Process
@login_required(login_url='/admin-login')
def refund(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    r = Refund.objects.all().order_by('-payment_date')
    context['data']=r
    return render(request, 'admin-refund.html', context)



# Refund Process
@login_required(login_url='/admin-login')
def changeStatus(request,id):
    if not request.user.is_staff:  # Check if the user is an admin or not
        return redirect('/admin-login')
    c = Refund.objects.get(id=id)
    c.status='Refunded'
    c.save()
    return redirect('/refund')