from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("login")

        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect("login")

        login(request, user)
        return redirect("dashboard")

    return render(request, "login.html")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")

        # Validate username or email
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return render(
                    request,
                    "forgot_password.html",
                    {"error": "No user found with this username or email!"},
                )

        # ---- SEND RESET EMAIL ----

        # Create secure UID + Token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Build full password reset URL
        current_site = get_current_site(request)
        reset_link = f"http://{current_site.domain}{reverse('reset_password', args=[uid, token])}"

        # Email content
        subject = "Password Reset Request"
        message = f"""
            Hello {user.username},

            We received a request to reset your password.

            Click the link below to reset it:

            {reset_link}

            If you did not request this, you can ignore this email.
            """

        # Send the mail
        send_mail(
            subject,
            message,
            "no-reply@yourwebsite.com",
            [user.email],
            fail_silently=False,
        )

        # Show success message OR redirect
        return render(
            request,
            "forgot_password.html",
            {"info": "A password reset link has been sent to your email."},
        )

    return render(request, "forgot_password.html")



def reset_password(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    # Invalid link: user not found or token wrong
    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired reset link!")
        return redirect("login")

    # POST — Save new password
    if request.method == "POST":
        pw1 = request.POST.get("password1")
        pw2 = request.POST.get("password2")

        if pw1 != pw2:
            messages.error(request, "Passwords do not match!")
            return redirect(request.path)

        if len(pw1) < 6:
            messages.error(request, "Password must be at least 6 characters!")
            return redirect(request.path)

        # Save new password
        user.set_password(pw1)
        user.save()

        messages.success(request, "Your password has been updated successfully!")
        return redirect("login")

    # GET — Show the form
    return render(request, "reset_password.html")
