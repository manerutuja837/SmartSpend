from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm


def profile_add(request):
    # Retrieve the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')  # Redirect to the profile page after saving
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile/profile.html', {'form': form})

def profile_view(request):
    user = UserProfile.objects.filter(user=request.user)
    if not user.exists():
        print("Hello")
        return redirect('profile')
    else:
        print("HI")
        user = UserProfile.objects.get(user=request.user)
        return render(request, 'profile/profile_view.html', {'user': user})