from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login , authenticate , logout
from .forms import StudentSignUpForm, TeacherSignUpForm, UserProfileUpdateForm, ProfileForm, ChangePasswordForm, ForgotPasswordForm
from .models import *
from q.models import *
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .utilis import *
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')  # Get OTP input from the user
        user_otp = request.session.get('otp')  # Get the OTP stored in session
        user_data = request.session.get('user_data')  # Retrieve user details from session
        
        if not user_data or not user_otp:
            return HttpResponse('No signup data found. Please sign up again.', status=400)

        # Check if the provided OTP matches the stored one
        if otp == user_otp:
            # Create and save the user after successful OTP verification
            user = User.objects.create(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                prn=user_data.get('prn', ''), 
                gender = user_data.get('gender') ,
                password=make_password(user_data['password']),  # Hash the password
                is_student=user_data.get('is_student', False),  # Set based on signup type
                is_teacher=user_data.get('is_teacher', False),  # Set based on signup type
                is_verified=True  # Mark the user as verified
            )
            
            # Clear session data after saving the user
            request.session.pop('user_data', None)
            request.session.pop('otp', None)
            
            login(request, user)

            # Redirect based on user type
            if user.is_student:
                return redirect('student_home')
            elif user.is_teacher:
                return redirect('teacher_home')
            
        else:
            return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')


def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            prn = form.cleaned_data.get('prn')
            gender = form.cleaned_data['gender']
            
            # Store user details in the session temporarily
            request.session['user_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'prn': prn,
                'gender' : gender ,
                'password': password,  # Optionally, hash the password now
                'is_student': True,  # For student signup
            }
            
            # Send OTP for email verification
            otp = send_otp_email(email)  # Send OTP to the email
            request.session['otp'] = otp  # Store the generated OTP in session for verification
            return redirect('verify_otp')
        else:
            # If the form is not valid, re-render the signup page with form errors
            return render(request, 'signup.html', {'form': form, 'user_type': 'Student'})
    
    else:
        form = StudentSignUpForm()
    return render(request, 'signup.html', {'form': form, 'user_type': 'Student'})


def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            gender = form.cleaned_data['gender']
            
            # Store user details in the session temporarily
            request.session['user_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'prn': "",  # Teachers don’t need a PRN
                'gender' : gender,
                'password': password,  # Optionally, hash the password now
                'is_teacher': True,  # For teacher signup
            }

            otp = send_otp_email(email)
            request.session['otp'] = otp  
            return redirect('verify_otp')
        else:
            return render(request, 'signup.html', {'form': form, 'user_type': 'Teacher'})
    
    else:
        form = TeacherSignUpForm()
    return render(request, 'signup.html', {'form': form, 'user_type': 'Teacher'})




# def verify_otp(request):
#     if request.method == 'POST':
#         otp = request.POST.get('otp')  # Get OTP input from the user
#         user_otp = request.session.get('otp')  # Get the OTP stored in session
#         user_data = request.session.get('user_data')  # Retrieve user details from session
        
#         if not user_data or not user_otp:
#             return HttpResponse('No signup data found. Please sign up again.', status=400)

#         # Check if the provided OTP matches the stored one
#         if otp == user_otp:
#             # Create and save the user after successful OTP verification
#             user = User.objects.create(
#                 username=user_data['username'],
#                 email=user_data['email'],
#                 prn=user_data['prn'],
#                 password=make_password(user_data['password']),  # Hash the password
#                 is_student=user_data.get('is_student', False),  # Set based on signup type
#                 is_teacher=user_data.get('is_teacher', False),  # Set based on signup type
#                 is_verified=True  # Mark the user as verified
#             )
            
#             # Clear session data after saving the user
#             request.session.pop('user_data', None)
#             request.session.pop('otp', None)
            
#             login(request, user)

#             if user.is_student:
#                 return redirect('student_home')
#             elif user.is_teacher:
#                 return redirect('teacher_home')
            
#         else:
#             return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

#     return render(request, 'verify_otp.html')

# def student_signup(request):
#     if request.method == 'POST':
#         form = StudentSignUpForm(request.POST)


#         if form.is_valid():
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password1']
#             prn = form.cleaned_data.get('prn')
            
#             # Store user details in the session temporarily
#             request.session['user_data'] = {
#                 'username': username,
#                 'email': email,
#                 'prn': prn,
#                 'password': password,  # Optionally, hash the password now
#                 'is_student': True,  # For student signup
#             }
            
#             # Send OTP for email verification
#             otp = send_otp_email(email)  # Send OTP to the email
#             request.session['otp'] = otp  # Store the generated OTP in session for verification
#             return redirect('verify_otp')
#         else:
#             # If the form is not valid, re-render the signup page with form errors
#             return render(request, 'signup.html', {'form': form, 'user_type': 'Student'})
    
#     else:
#         form = StudentSignUpForm()
#     return render(request, 'signup.html', {'form': form, 'user_type': 'Student'})

# def teacher_signup(request):
#     if request.method == 'POST':
#         form = TeacherSignUpForm(request.POST)

#         if form.is_valid():
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password1']
            
#             request.session['user_data'] = {
#                 'username': username,
#                 'email': email,
#                 'prn': "" ,
#                 'password': password,  # Optionally, hash the password now
#                 'is_teacher': True,  # For teacher signup
#             }

#             otp = send_otp_email(email)  
#             request.session['otp'] = otp  
#             return redirect('verify_otp')
#         else:
#             return render(request, 'signup.html', {'form': form, 'user_type': 'Teacher'})
    
#     else:
#         form = TeacherSignUpForm()
#     return render(request, 'signup.html', {'form': form, 'user_type': 'Teacher'})


def check_email_exists_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})

def check_prn_exists(request):
    prn = request.GET.get('prn')
    exists = User.objects.filter(prn=prn).exists()  # Check if PRN exists in the Student model
    return JsonResponse({'exists': exists})

def check_email_exists(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()  # Check if email exists in the User model
    return JsonResponse({'exists': exists})

def login_view(request):
    if request.method == "POST":
        # Only pass 'data=request.POST' to the form
        form = CustomLoginForm(data=request.POST)  
        if form.is_valid():
            email = form.cleaned_data.get('email')  # Get email instead of username
            password = form.cleaned_data.get('password')
            
            # Fetch the user by email
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                user = None
            
            if user is not None:
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    if user.is_student:
                        return redirect('student_home')
                    elif user.is_teacher:
                        return redirect('teacher_home')
            
        # Handle invalid form (wrong email or password)
        form.add_error(None, "Invalid email or password.")
    
    else:
        if request.user.is_authenticated:
            if request.user.is_student:
                return redirect('student_home')
            elif request.user.is_teacher:
                return redirect('teacher_home')
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})



def root(request):
    user = request.user
    if request.user.is_authenticated:
        if user.is_student:
            return redirect('student_home')
        elif user.is_teacher:
            return redirect('teacher_home')
    return render(request , 'landing2.html', {'user' : user})

@login_required
def request_password_change(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)  # Pass the current user

        if form.is_valid():
            new_password = form.cleaned_data['new_password']

            # Send OTP to user's email
            otp = send_otp_email(request.user.email)
            request.session['password_change_data'] = {
                'new_password': new_password,
            }
            request.session['otp'] = otp  # Store OTP in session for verification

            return redirect('verify_password_change_otp')
    else:
        form = ChangePasswordForm(user=request.user)  # Pass the user to the form

    return render(request, 'request_password_change.html', {'form': form})






def check_old_password(request):
    new_password = request.GET.get('new_password', '')
    user = request.user

    if check_password(new_password, user.password):
        return JsonResponse({'is_same_as_old': True})
    else:
        return JsonResponse({'is_same_as_old': False})






def verify_password_change_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_otp = request.session.get('otp')
        password_change_data = request.session.get('password_change_data')

        if not password_change_data or not user_otp:
            return HttpResponse('No password change data found. Please try again.', status=400)

        if otp == user_otp:
            new_password = password_change_data['new_password']

            # Update the user's password
            user = request.user
            user.set_password(new_password)  # Set the new password
            user.save()

            # Clear session data after password change
            request.session.pop('password_change_data', None)
            request.session.pop('otp', None)

            # Log the user out after changing the password
            logout(request)

            messages.success(request, 'Your password has been updated successfully. Please log in with your new password.')

            return redirect('login')
        else:
            return render(request, 'verify_password_change_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_password_change_otp.html')

# def send_otp_email(email):
#     otp = str(random.randint(100000, 999999))  
#     send_mail(
#         'OTP From QuizBOT.',
#         f'Your OTP is : {otp}',
#         'your-email@example.com',
#         [email],
#         fail_silently=False,
#     )
#     return otp  # Return the OTP to store it in session for 

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if the email exists in the user model
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                
                # Generate OTP or reset token
                otp = send_otp_email(email)  # You can use token-based reset if preferred
                
                # Save OTP or token in session for validation
                request.session['reset_password_email'] = email
                request.session['otp'] = otp
                
                return redirect('verify_reset_otp')  # Redirect to OTP verification
            else:
                messages.error(request, "Email does not exist.")
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})

def verify_reset_otp(request):
    # if request.method == 'POST':
    #     otp = request.POST.get('otp')
    #     user_otp = request.session.get('otp')
    #     email = request.session.get('reset_password_email')

    #     if not email or not user_otp:
    #         messages.error(request, "Session expired. Please try again.")
    #         return render(request, 'verify_reset_otp.html')

    #     if otp == user_otp:
    #         # Redirect to password reset form
    #         return redirect('reset_password')
    #     else:
    #         messages.error(request, "Invalid OTP. Please try again.")

    if request.method == 'POST':
        otp = request.POST.get('otp') 
        user_otp = request.session.get('otp')        

        if otp == user_otp:
            request.session.pop('otp', None)
            return redirect('reset_password')
        else:
            return render(request, 'verify_reset_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_reset_otp.html')

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            email = request.session.get('reset_password_email')
            user = User.objects.get(email=email)

            # Update the user's password
            user.password = make_password(new_password)
            user.save()

            # Clear session data
            request.session.pop('reset_password_email', None)
            request.session.pop('otp', None)

            messages.success(request, 'Password has been reset successfully.')
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'reset_password.html', {
        'new_password_error': messages.get_messages(request),
        'confirm_password_error': messages.get_messages(request)
    })

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=user)
        if profile_form.is_valid():
            user = profile_form.save(commit=False)
            if profile_form.cleaned_data.get('password'):
                user.set_password(profile_form.cleaned_data['password'])
                update_session_auth_hash(request, user)
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile_view')
    else:
        profile_form = ProfileForm(instance=user)

    if user.is_student:
        return render(request, 'profile_student.html', {'profile_form': profile_form})
    elif user.is_teacher:
        return render(request, 'profile_teacher.html', {'profile_form': profile_form})
    else:
        return render(request, 'profile.html', {'profile_form': profile_form})  # Default for any other type

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def home_std(request):
    user = request.user
    if request.user.is_authenticated:
        if user.is_teacher:
            return redirect('teacher_home')
    result = QuizResult.objects.filter(user=user)
    return render(request, 'dashboard_std.html', {'results': result})
    # return render(request, 'dashboard.html')

@login_required
def home_tea(request):
    # user = request.user
    user = request.user
    if request.user.is_authenticated:
        if user.is_student:
            return redirect('student_home')
    quiz = Quiz.objects.filter(host=user)
    return render(request, 'dashboard_tea.html', {'quizzes': quiz})
    # return render(request, 'dashboard.html')

def logout_view(request):
    if request.method == 'POST' :
        logout(request)
        return redirect('landing')
    
    return render(request , 'logout.html')
