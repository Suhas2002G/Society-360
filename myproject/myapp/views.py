from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User        
from django.contrib.auth import authenticate       
from django.contrib.auth import login,logout
from myapp.models import Notice,Flat,Amenity,Poll
from django.db.models import Q  
import logging
from django.utils import timezone
from datetime import date
import razorpay
from django.core.mail import send_mail 


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




def owner_home(request):
    context={}

    return render(request, 'owner-home.html', context)


def owner_notice(request):
    context={}
    notices = Notice.objects.all().order_by('-created_at')
    context['notices'] = notices
    return render(request, 'owner-notice.html', context)


def owner_book_amenity(request):
    context={}
    try:
        amenities = Amenity.objects.all()  # Fetching all amenities
        context['amenities'] = amenities
    except Exception as e:
        context['errormsg'] = f"Error fetching amenities: {e}"

    return render(request, 'owner-bookamenity.html', context)


# Owner can Raise Complaint
def owner_raise_complaint(request):
    if request.method == 'GET':
        return render(request, 'owner-raise-complaint.html')
    else:
        pass



# Owner Maintenance Payment
def owner_maintenance(request):
   pass



# Makepayment
def makepayment(request,amount_to_pay):
    context={}
    amt = amount_to_pay
    client = razorpay.Client(auth=("rzp_test_c66P03WlENQIxJ", "Om1tOy0A2HuYZUT0rHFnZgTd"))

    amt = int(float(amt) * 100) # to convert amount to paise 

    data = { "amount": amt, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context['payment']=payment
    #print(payment)      #check whether amount is printing on terminal 
    # return HttpResponse("Amount Fetched")

    # Get the current date
    current_date = timezone.now().date()
    
    # Get the current month (using the first day of the month for easy comparison)
    current_month = date(current_date.year, current_date.month, 1)

    payment_date = current_date

    payment = MaintenancePayment(
            uid=request.user,
            month=current_month,
            payment_date=payment_date,
            amount=amount_to_pay,
            # penalty=penalty
        )
    payment.save() 
    
    return render(request, 'pay.html', context)
    


# # Payment-Success page after paying Maintenance & Email Integration
def paymentsuccess(request):
    
    sub='Society360 Monthly Maintenance'
    msg="We have received monthly maintenance from your side. Thank you..! "
    frm='suhas8838@gmail.com'

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
def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin')
    return render(request, 'admin-dashboard.html')


def admin_add_notice(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'admin-addnotice.html', context)
    else:
        # title = request.POST.get('title', '').strip()
        # cat = request.POST.get('category', '').strip()
        # des = request.POST.get('description', '').strip()
        # priority = request.POST.get('priority', '').strip()
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




def admin_usermanage(request):
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



def admin_add_amenity(request):
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
def admin_view_amenity(request):
    context = {}
    try:
        amenities = Amenity.objects.all()  # Fetching all amenities
        context['amenities'] = amenities
    except Exception as e:
        context['errormsg'] = f"Error fetching amenities: {e}"

    return render(request, 'admin-viewAmenity.html', context)


# Delete particular Amenity
def admin_delete_amenity(request,aid):
    context = {}
    amenity = Amenity.objects.filter(id=aid)
    amenity.delete()
    return redirect('/admin-view-amenity')
    

# Admin View Notice
def admin_view_notice(request):
    context = {}
    try:
        # Fetching all notices
        notices = Notice.objects.all().order_by('-created_at')
        context['notices'] = notices
    except Exception as e:
        context['errormsg'] = f"Error fetching notices: {e}"

    return render(request, 'admin-viewnotice.html', context)



def admin_delete_notice(request,nid):
    context = {}
    notice = Notice.objects.filter(id=nid)
    # print(notice)
    # return HttpResponse('fetched')
    notice.delete()
    return redirect('/admin-viewnotice')



# Admin Add poll
def admin_add_poll(request):
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

        

