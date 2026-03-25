from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, Profileform
from .models import Profile


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'authentication/registration.html', context)


@login_required
def addprofile(request):
    if request.method == 'POST':
        form = Profileform(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('/')
    else:
        form = Profileform()
    context = {'form': form}
    return render(request, 'authentication/profile.html', context)


@login_required
def updateprofile(request, id):
    updateP = get_object_or_404(Profile, id=id)
    form = Profileform(request.POST or None, request.FILES or None, instance=updateP)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect('/')
    context = {'form': form}
    return render(request, 'authentication/profile.html', context)
