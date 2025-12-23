from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
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


from .core.config import settings
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required

# 
from .services import NoticeSection, AmenityService, ComplaintService, NotificationService, MaintenanceService
#

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

    # Validate username: alphabets only
    if not uname.replace(" ", "").isalpha():
        context['errormsg'] = 'Username must contain alphabets only.'
        return render(request, 'owner-register.html', context)

    # Check password len
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
        context['errormsg'] = 'User with this email/mobile already exists.'

    except ValidationError as e:
        logger.error(f"ValidationError: {e.messages}")
        context['errormsg'] = f'Invalid data: {e.messages[0]}'

    except Exception as e:
        logger.error("Unexpected error during owner registration")
        context['errormsg'] = 'Unexpected error occurred. Please try again later.'

    return render(request, 'owner-register.html', context)
    


def owner_login(request):
    """
    Handle login functionality for flat owners.

    HTTP Methods:
        - GET  : Render the login form.
        - POST : Validate user credentials and authenticate the user.

    Returns HttpResponse:
        - Renders 'owner-login.html' with error messages if login fails.
        - Redirects to '/owner-home' if authentication succeeds.
    """
    context={}

    # Handle GET request (display login form)
    if request.method == 'GET':
        return render(request,'owner-login.html')
    
    # Handle POST request (process login form)
    try:
        email = request.POST.get('ue', '').strip()
        password = request.POST.get('upass', '').strip()

        # Basic validation
        if not email or not password:
            context['errormsg'] = 'Please fill in both fields.'
            logger.warning("Login attempt with empty fields.")
            return render(request, 'owner-login.html', context)
        
        # Authenticate user
        user = authenticate(username=email, password=password)

        if user is not None:
            login(request,user)        # Login Method
            logger.info(f"User '{email}' logged in successfully.")
            return redirect('/owner-home')
        else:
            context['errormsg'] = 'Invalid credentials.'
            logger.warning(f"Failed login attempt for email: {email}")
            return render(request, 'owner-login.html', context)
    except Exception as e:
        logger.error(f"Unexpected error during login for email '{email}': {e}")
        context['errormsg'] = 'An unexpected error occurred. Please try again later.'
        return render(request, 'owner-login.html', context)



def owner_logout(request):
    """
    Log out the currently authenticated user.

    This view clears the session and redirects to the home page.

    Returns:
        HttpResponseRedirect: Redirects to '/' after logout.
    """
    try:
        user_email = request.user.email if request.user.is_authenticated else 'Anonymous'
        logout(request)  # Clear the session
        logger.info(f"User '{user_email}' logged out successfully.")
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")

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
            
            try:
                notification = NotificationService
                # Send OTP to user email
                notification.send_email(
                    subject='Reset Password',
                    messsage=f"Your OTP for password reset is: {otp}",
                    to_email=[e]

                ) 
            except Exception as e:
                logger.error(f'Failed to send OTP: {str(e)}')

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





#----------------------------------------
#       OWNER HOME PAGE NOTICE SECTION
#----------------------------------------

@login_required(login_url='/owner-login')
def owner_home(request):
    """
    Display the Owner Home Page.

    Fetches the latest 2 notices and passes them to the template.

    Returns:
        HttpResponse: Renders 'owner-home.html' with notice context.
    """
    context={}

    try:
        # Fetch latest 2 notices ordered by creation date
        notices = NoticeSection.fetch_latest_notices(limit=2)
        context['notice']=notices
    except Exception as e:
        logger.error(f"Error fetching notices for owner: {e}")
        context['errormsg'] = "Unable to load notices at this time. Please try again later."
    
    return render(request, 'owner-home.html', context)



#----------------------------------------
#       NOTICE SECTION PAGE
#----------------------------------------

# Notice Board for Owner
@login_required(login_url='/owner-login')
def owner_notice(request):
    """
    Display the notice board for owners.

    Fetches all notices ordered by creation date (most recent first) 
    and passes them to the 'owner-notice.html' template.

    Returns:
        HttpResponse: Renders 'owner-notice.html' with notices context.
    """
    context = {}

    try:
        # Fetch all notices in descending order of creation date
        notices = NoticeSection.fetch_latest_notices()
        print(notices)
        context['notices'] = notices
        logger.info(f"Notices fetched: {notices.count()}")

    except Exception as e:
        logger.error(f"Error fetching notices for owner: {e}")
        context['errormsg'] = "Unable to load notices at this time. Please try again later."

    return render(request, 'owner-notice.html', context)



#----------------------------------------
#       MAINTENANCE SECTION [PENDING]
#----------------------------------------

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
    RAZORPAY_API_KEY = settings.RAZORPAY_API_KEY
    RAZORPAY_API_PASS = settings.RAZORPAY_API_PASS

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

    u=User.objects.filter(id=request.user.id)    #email should go to authenticated user only 
    to=u[0].email
    print(u)            #<QuerySet [<User: suhas8838@gmail.com>]>
    print(u[0].email)   #suhas8838@gmail.com

    fid = Flat.objects.get(uid=request.user.id)
    # print(fid)



    notification = NotificationService()
    notification.send_email(
        subject='Society360 Monthly Maintenance',
        message="We have received monthly maintenance from your side. Thank you..! ",
        to_email=[to]
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



#----------------------------------------
#       AMENITY BOOKING SECTION PAGE
#----------------------------------------

# Owner View Book Amenity
@login_required(login_url='/owner-login')
def owner_book_amenity(request):
    """
    Display all available amenities for the owner to book.

    Fetches all Amenity objects and passes them to the
    'owner-bookamenity.html' template.

    Returns:
        HttpResponse: Rendered template with amenities context.
    """
    context={}

    try:
        # Fetch all amenities
        amenities = Amenity.objects.all()  
        context['amenities'] = amenities
        logger.info(f"Total amenities: {amenities.count()}")

    except Exception as e:
        logger.error(f"Error fetching amenities: {e}")
        context['errormsg'] = "No amenities found at this time."

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

            RAZORPAY_API_KEY = settings.RAZORPAY_API_KEY
            RAZORPAY_API_PASS = settings.RAZORPAY_API_PASS

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
    u=User.objects.filter(id=request.user.id)  #email should go to authenticated user only 
    to=u[0].email


    notification = NotificationService()
    notification.send_email(
        subject='Society360 Amenity Booking Confirmation',
        message="We have received your booking for amenity from your side. Thank you..! ",
        to_email=[to]
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



#----------------------------------------
#       COMPLAINT SECTION PAGE
#----------------------------------------

# Owner View Complaint
@login_required(login_url='/owner-login')
def owner_view_complaint(request):
    """
    View for displaying complaints submitted by the logged-in owner.

    Fetches complaints for the authenticated user and passes them to the template.
    Handles errors gracefully by logging them and showing a safe fallback message.
    """
    context={}
    try:
        complaints = ComplaintService.fetch_complaints(user_id=request.user.id)
        context['data']=complaints 
    except Exception as e:
        logger.error(f"Error fetching complaints: {e}")
        context['errormsg'] = "Unable to load complaints at this time. Please try again later."
    return render(request, 'owner-view-complaint.html', context)



# Owner can Raise Complaint
@login_required(login_url='/owner-login')
def owner_raise_complaint(request):
    """
    View for raising a new complaint by the logged-in owner.

    Handles GET requests to display the form and POST requests to submit the complaint.
    Returns the appropriate response depending on success or validation failure.
    """
    context={}

    if request.method == 'GET':
        return render(request, 'owner-raise-complaint.html')
    
    # POST request:
    title = request.POST.get("title", "").strip()
    category = request.POST.get("category", "").strip()
    description = request.POST.get("description", "").strip()


    try:
        ComplaintService.create_complaint(
            title=title,
            category=category,
            description=description,
            user=request.user
        )
        context["success"] = "Complaint raised successfully."
    except ValueError as ve:
        logger.error(str(ve))
        context["errormsg"] = str(ve)
    except Exception as exc:
        logger.error(f"Error creating complaint: {exc}")
        context["errormsg"] = "Something went wrong. Please try again later."

    return render(request, "owner-raise-complaint.html", context)


#----------------------------------------
#       Emergency Contact SECTION PAGE
#----------------------------------------

@login_required(login_url='/owner-login')
def owner_emerg_contact(request):
    context={}
    return render(request, 'owner-emerg-contact.html', context)













#````````````````````````````````````````````````````````````
#~~~~~~~~~~~~~~~~~~~~~  ADMIN PART  ~~~~~~~~~~~~~~~~~~~~~~~~#
#............................................................


# Admin Login
def admin_login(request):
    '''Login function to authenticate user has admin privilages or not'''
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
@staff_member_required(login_url='/admin-login')
def admin_dashboard(request):
    '''Admin dashboard with owner_count, payment_amount, and basic bar-chart'''
    context={}
    try:
        # Current date (without time)
        current_date = timezone.localdate()

        # Summary counts
        owner_count = Flat.objects.count()
        notice_count = Notice.objects.count()
        comp_count = Complaint.objects.count()

        
        # Total maintenance amount (use aggregate)
        total_maintenance = (
            MaintenancePayment.objects.aggregate(total=Sum('amount'))['total'] or 0
        )

        # Aggregate maintenance payments by month
        monthly_payments = (
            MaintenancePayment.objects
            .annotate(month=TruncMonth('payment_date'))  # Extract month from payment_date
            .values('month')                            # Group by month
            .annotate(total_amount=Sum('amount'))       # Sum amounts for each month
            .order_by('month')                          # Order by month
        )

        # Prepare data for chart (for JS)
        months = []
        amounts = []

        for entry in monthly_payments:
            month = entry['month']
            total = entry['total_amount'] or 0
            # Format month like "Jan 2025"
            months.append(month.strftime('%b %Y'))
            amounts.append(float(total))

        # Final context
        context.update({
            'ocount': owner_count,
            'ncount': notice_count,
            'compCount': comp_count,
            'current_date': current_date,
            'mamount': total_maintenance,
            'months': months,
            'amounts': amounts,
        })

        logger.debug(context)

    except Exception as exc:
        logger.exception("Dashboard data fetching failed.")

    return render(request, 'admin-dashboard.html', context)


#----------------------------------------
#       ADMIN NOTICE SECTION 
#----------------------------------------

# Admin View Notice
@staff_member_required(login_url='/admin-login')
def admin_view_notice(request):
    """
    Admin view for displaying all notices.

    Retrieves all notices (ordered newest first) using the NoticeService layer
    and renders them in the admin notice list page. If any error occurs during
    fetching, it logs the error and sends a safe fallback message to the UI.

    Args:
        request (HttpRequest): The incoming request instance from the admin user.

    Returns:
        HttpResponse: Renders `admin-viewnotice.html` with notice data or an error message in case of failure.
    """
    context = {}
    try:
        # Fetching all notices
        notices = NoticeSection.fetch_latest_notices()
        context['notices'] = notices
        logger.info(f"Notices fetched for admin: {notices.count()}")

    except Exception as e:
        logger.error(f"Error fetching notices: {e}")
        context['errormsg'] = "Unable to load notices at this time. Please try again later."

    return render(request, 'admin-viewnotice.html', context)



# Delete particular notice
@staff_member_required(login_url='/admin-login')
def admin_delete_notice(request, nid: int):
    """
    Admin view to delete a specific notice.

    Attempts to delete the notice identified by 'nid' using the NoticeService.
    Logs any errors that occur during deletion. Regardless of success or failure,
    redirects the admin back to the notice list page.

    Args:
        request (HttpRequest): The incoming HTTP request.
        nid (int): The ID of the notice to be deleted.

    Returns:
        HttpResponseRedirect: Redirects to the admin notice listing page.
    """
    try:
        deleted_count = NoticeSection.delete_notice_by_id(notice_id=nid)
        if deleted_count == 0:
            logger.warning(f"Admin delete notice: No notice found with id={nid}")
    except Exception as exc:
        logger.error(f"Error deleting notice with id={nid}: str{exc}")

    return redirect("/admin-viewnotice")



# Admin Add New Notice
@staff_member_required(login_url='/admin-login')
def admin_add_notice(request):
    """
    Handle the creation of new administrative notices.

    This view is accessible only to authenticated staff users.  
    It serves two purposes based on the request method:

    - GET Request:  
      Renders the "Add Notice" form allowing the admin to input notice details.

    - POST Request: 
      Validates form input and, if valid:
        1. Creates a new `Notice` record using the service layer (`NoticeSection`).
        2. Sends an SMS notification (optional) via `NotificationService`.
        3. Displays a success message if stored successfully,
           or shows an error message if something goes wrong.
    """
    
    context = {}
    if request.method == 'GET':
        return render(request, 'admin-addnotice.html', context)
    
    # POST Method
    title = request.POST.get('title', '').strip()
    category = request.POST.get('category', '').strip()
    description = request.POST.get('description', '').strip()
    priority = request.POST.get('priority', 'None').strip()

    # Basic validation
    if not title or not category or not description:
        context['errormsg'] = 'Please fill all the fields.'
        return render(request, 'admin-addnotice.html', context)

    try:
        # Create notice
        notice = NoticeSection.create_notice(
            title=title,
            category=category,
            description=description,
            priority=priority,
        )

        # Send SMS notification (optional failure – app continues)
        notification_service = NotificationService()
        try:
            message = notification_service.send_sms()
            if message:
                print(f"SMS sent successfully. SID: {message.sid}")
        except Exception as sms_error:
            # Don’t break the flow if SMS fails – just log it
            print(f"Failed to send SMS notification: {sms_error}")

        context['successmsg'] = 'Notice has been successfully posted..!'

    except Exception as e:
        print(f"Error while creating notice: {e}")
        logger.warning(f"Error while creating notice: {e}")
        context['errormsg'] = 'An error occurred. Please try again later.'

    return render(request, 'admin-addnotice.html', context)


#----------------------------------------
#       ADMIN MAINTENANCE DASHBOARD SECTION 
#----------------------------------------

# Admin Maintenance Management
@staff_member_required(login_url='/admin-login')
def admin_maintenance(request):
    """
    Display the maintenance dashboard with all payment records.

    Accessible only by admin (staff) users. This view queries the maintenance 
    records from the database using the service layer and returns them for 
    display on the admin maintenance management page.

    Behavior:
    - On success: Loads the maintenance table with stored payment records.
    - On failure: Logs the error and returns an error message to the UI.

    """
    context = {}

    try:
        maintenance_service = MaintenanceService()
        maintenance_records = maintenance_service.fetch_maintenance_records()
        context['data'] = maintenance_records
    except Exception as e:
        logger.error(f"Failed to fetch maintenance records: {e}")
        context['errormsg'] = 'An error occurred. Please try again later.'

    return render(request, 'admin-maintenance.html', context)



# Admin Maintenance Dashboard Filter
@staff_member_required(login_url='/admin-login')
def admin_maintenance_filter(request):
    """
    Filter maintenance payment records based on admin-selected criteria.

    Filters available:
        - Flat number
        - Owner name
        - Date range

    Returns the filtered result back to the maintenance dashboard.
    """
    try:
        context = {}
        # Extract filter values safely
        flatno = request.POST.get('flatno', '').strip()
        ownername = request.POST.get('oname', '').strip()
        start_date = request.POST.get('start_date', '').strip()
        end_date = request.POST.get('end_date', '').strip()

        service = MaintenanceService()
        filtered_records = service.filter_maintenance_records(
            flatno=flatno,
            ownername=ownername,
            start_date=start_date,
            end_date=end_date
        )
        logger.info('Records are filtered')
        return render(request, 'admin-maintenance.html', {'data': filtered_records})
    except Exception as e:
        logger.error(f"Failed to filter maintenance records: {e}")
        context['errormsg'] = 'An error occurred. Please try again later.'
        return render(request, 'admin-maintenance.html', context)


#----------------------------------------
#       ADMIN AMENITY MANAGEMENT SECTION 
#----------------------------------------

# Admin Add New Amenity
@staff_member_required(login_url='/admin-login')
def admin_add_amenity(request):
    """Admin can add a new amenity."""
    
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
                AmenityService.create_amenity(
                    amenity_name=amenity_name,
                    description=description,
                    rent=rent,
                    img=img,
                )
                context['successmsg'] = "Amenity added successfully!"
            except Exception as e:
                context['errormsg'] = f"Error adding amenity: {e}"

    return render(request, 'admin-addAmenity.html', context)



# Admin View Amenity
@staff_member_required(login_url='/admin-login')
def admin_view_amenity(request):
    """Admin can see all amenities."""
    context = {}
    try:
        amenities = AmenityService.list_amenities()
        context['amenities'] = amenities
    except Exception as e:
        logger.error(f"Error fetching amenities: {e}")
        context['errormsg'] = f"Error fetching amenities: {e}"

    return render(request, 'admin-viewAmenity.html', context)



# Delete particular Amenity
@staff_member_required(login_url='/admin-login')
def admin_delete_amenity(request,aid):
    """Admin can delete a particular amenity."""
    try:
        AmenityService.delete_amenity(aid)
    except Exception as e:
        logger.error(f"Error fetching amenities: {e}")
    finally:    
        return redirect('/admin-view-amenity')
    


# Edit particular Amenity
@staff_member_required(login_url='/admin-login')
def admin_edit_amenity(request, aid):
    """Admin can edit a particular amenity."""
    context = {}
    try:
        amenity = AmenityService.get_amenity(aid)
        
        if request.method == 'GET':
            # For template compatibility with your original `[amenity]`
            context['data'] = [amenity]  
        
        elif request.method == 'POST':
            amenity_name = request.POST.get('amenity')
            description = request.POST.get('description')
            rent = request.POST.get('rent')
            img = request.FILES.get('img') if 'img' in request.FILES else None

            updated_amenity = AmenityService.update_amenity(
                aid=aid,
                amenity_name=amenity_name,
                description=description,
                rent=rent,
                img=img,
            )

            context['data'] = [updated_amenity]
            context['successmsg'] = "Amenity updated successfully!"

    except Amenity.DoesNotExist:
        logger.error('Amenity not found!')
        context['errormsg'] = "Amenity not found!"

    return render(request, 'admin-editAmenity.html', context)



# Admin can see all bookings
@staff_member_required(login_url='/admin-login')
def admin_booking(request):
    """Admin can see all amenity bookings."""
    context = {}
    bookings = AmenityService.list_bookings()
    context['data'] = bookings
    return render(request, 'admin-booking-page.html', context)



#----------------------------------------
#       ADMIN COMPLAINT MANG. SECTION 
#----------------------------------------

# Complaint Lists
@staff_member_required(login_url='/admin-login')
def admin_manage_complaint(request):
    '''Admin can manage tenant complaints on dashboard'''
    context={}
    c = Complaint.objects.all().order_by('-created_at')
    context['data']=c 
    return render(request, 'admin-manage-complaint.html', context)



#----------------------------------------
#       ADMIN AMOUNT REFUND SECTION 
#----------------------------------------
# Refund Process
@staff_member_required(login_url='/admin-login')
def refund(request):    
    context={}
    r = Refund.objects.all().order_by('-payment_date')
    context['data']=r
    return render(request, 'admin-refund.html', context)



# Refund Process
@staff_member_required(login_url='/admin-login')
def changeStatus(request,id):
    if not request.user.is_staff:  # Check if the user is an admin or not
        return redirect('/admin-login')
    c = Refund.objects.get(id=id)
    c.status='Refunded'
    c.save()
    return redirect('/refund')



#----------------------------------------
#       ADMIN OWNER MANAGEMENT SECTION 
#----------------------------------------

# Admin can do Owner Management
@staff_member_required(login_url='/admin-login')
def admin_usermanage(request):
    
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

