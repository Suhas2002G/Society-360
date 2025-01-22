from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.contrib.auth.models import User        
from django.contrib.auth import authenticate       
from django.contrib.auth import login,logout
from myapp.models import Notice,Flat,Amenity,Poll, MaintenancePayment, BookingAmenity
from django.utils import timezone
from django.db.models import Q  
from datetime import date
import os
import razorpay
from django.core.mail import send_mail 
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
            # print('Password and Confirm password must be same')
            context['errormsg']='Password and Confirm password must be same'
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



# Owner view Poll and Surveys
@login_required(login_url='/owner-login')
def owner_view_poll(request):
    context={}
    p=Poll.objects.all().order_by('-created_at')
    context['data']=p
    return render(request, 'owner-view-poll.html', context)



# Owner can Vote for Poll and Surveys
@login_required(login_url='/owner-login')
def vote(request, vid, op):
    # Fetch the poll using get_object_or_404 to handle invalid poll IDs
    poll = get_object_or_404(Poll, id=vid)
    
    # Update the vote count for the selected option
    if op == '1':    
        poll.votes_1 += 1
    elif op == '2':  
        poll.votes_2 += 1
    
    poll.save()  

    # Calculate percentages after voting
    total_votes = poll.votes_1 + poll.votes_2
    if total_votes > 0:
        percentage_1 = (poll.votes_1 / total_votes) * 100
        percentage_2 = (poll.votes_2 / total_votes) * 100
    else:
        percentage_1 = 0
        percentage_2 = 0

    # Redirect the user to the polls listing page after voting
    return redirect('/owner-view-poll')   
        



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
    amount = 1000
    context={}
    RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
    RAZORPAY_API_PASS = os.getenv('RAZORPAY_API_PASS')

    # print(RAZORPAY_API_KEY)
    # print(RAZORPAY_API_PASS)

    amt = amount
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

    u=User.objects.filter(id=request.user.id)       #email should go to authenticated user only 
    to=u[0].email

    send_mail(
        sub,
        msg,
        frm,
        [to],               #list beacause we can send mail to multiple emails-ids
        fail_silently=False
    )

    # Insert a record in the MaintenancePayment model
    payment_data = {
        'uid': request.user,  # Assuming the user who made the payment
        # 'month': timezone.now().date(),  # Current month  
        'payment_date': timezone.now().date(),  # Current date of payment
        'amount': 1000,  # Amount paid (pass as parameter from Razorpay response)
    }
    
    # Create and save the MaintenancePayment record
    MaintenancePayment.objects.create(**payment_data)

    return render(request, 'paymentsuccess.html')






# Owner can Raise Complaint
@login_required(login_url='/owner-login')
def owner_raise_complaint(request):
    if request.method == 'GET':
        return render(request, 'owner-raise-complaint.html')
    else:
        pass













#~~~~~~~~~~~~~~~~~~~~~  ADMIN PART  ~~~~~~~~~~~~~~~~~~~~~~~~#


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

        mamount = 0
        m=MaintenancePayment.objects.all()
        for i in m:
            mamount += i.amount
        
        context={
            'ocount': ownerCount,
            'ncount' : noticeCount,
            'current_date' : current_date,
            'mamount' : mamount
            # 'compCount':complaintCount,
        }
        return render(request, 'admin-dashboard.html', context)



@login_required(login_url='/admin-login')
def admin_add_notice(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context = {}
    if request.method == 'GET':
        return render(request, 'admin-addnotice.html', context)
    else:
        title = request.POST['title']
        cat = request.POST['category']
        des = request.POST['description']
        priority = request.POST['priority']

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


@login_required(login_url='/admin-login')
def admin_maintenance(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    m = MaintenancePayment.objects.all().order_by('-payment_date')
    context['data'] = m
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



# Admin can see all bookings
@login_required(login_url='/admin-login')
def admin_booking(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    b = BookingAmenity.objects.all()
    context['data']=b
    return render(request, 'admin-booking-page.html', context)




# Admin Poll and Surveys
@login_required(login_url='/admin-login')
def admin_add_poll(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    if request.method=='GET':
        return render(request,'admin-add-poll.html')
    else:
        q=request.POST['question']
        op1=request.POST['option1']
        op2=request.POST['option2']

        if q=='' or op1=='' or op2=='' :
            context['errormsg']='Please fill all the fields'
        else:
            p=Poll.objects.create(question=q,option_1=op1,option_2=op2)
            p.save()
            context['successmsg']='Poll has been posted successfully..!'
        return render(request,'admin-add-poll.html',context)

        

# Admin View Poll 
@login_required(login_url='/admin-login')
def admin_view_poll(request):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    context={}
    p=Poll.objects.all().order_by('-created_at')
    context['data']=p
    return render(request, 'admin-view-poll.html', context)


# Admin can delete particular Poll
@login_required(login_url='/admin-login')
def admin_delete_poll(request,pid):
    if not request.user.is_staff:  # Check if the user is an admin
        return redirect('/admin-login')
    
    poll = Poll.objects.filter(id=pid)
    poll.delete()
    return redirect('/admin-view-poll')
