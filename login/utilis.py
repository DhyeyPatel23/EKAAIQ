import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))



def send_otp_email(email):
    """Send OTP to the provided email."""
    otp = generate_otp()
    subject = 'Your OTP for Email Verification'
    message = f'Your OTP for verification is {otp}.'
    from_email = 'quizbot9843@gmail.com'  # Replace with your actual email
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    return otp 