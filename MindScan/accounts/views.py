from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, LijecnikForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user_type = form.cleaned_data['user_type']

            if user_type == 'lijecnik':
                lijecnik_form = LijecnikForm(request.POST, request.FILES)
                if lijecnik_form.is_valid():
                    lijecnik = lijecnik_form.save(commit=False)
                    lijecnik.user = user
                    lijecnik.odobren = False  
                    lijecnik.save()
                    login(request, user)
                    return redirect('home')
                else:
                    return render(request, 'accounts/register.html', {
                        'form': form,
                        'lijecnik_form': lijecnik_form,
                    })
            else:
                login(request, user)
                return redirect('home')
        else:
            lijecnik_form = LijecnikForm()
            return render(request, 'accounts/register.html', {'form': form, 'lijecnik_form': lijecnik_form})
    else:
        form = CustomUserCreationForm()
        lijecnik_form = LijecnikForm()
    return render(request, 'accounts/register.html', {'form': form, 'lijecnik_form': lijecnik_form})




def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    else:
        return redirect('home')


