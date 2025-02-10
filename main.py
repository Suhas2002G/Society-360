import razorpay
import os

RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
RAZORPAY_API_PASS = os.getenv('RAZORPAY_API_PASS')



# Test Razorpay API integration
client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_PASS))

data = {
    "amount": 1000,  # Example: 10 INR (converted to paise)
    "currency": "INR",
    "receipt": "order_rcptid_11"
}

try:
    payment = client.order.create(data=data)
    print(payment)
except razorpay.errors.RazorpayError as e:
    print("Error:", e)
