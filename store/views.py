from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid credentials")
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
