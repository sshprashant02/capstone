import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import Cause, Donation, DonorProfile
from decimal import Decimal, InvalidOperation

def home(request):
    causes = Cause.objects.filter(is_active=True)
    return render(request, 'core/home.html', {'causes': causes})


def cause_detail(request, pk):
    cause = get_object_or_404(Cause, pk=pk)
    donations = Donation.objects.filter(cause=cause, status='completed').order_by('-donated_at')[:10]
    return render(request, 'core/cause_detail.html', {'cause': cause, 'donations': donations})


@login_required
def donate(request, pk):
    cause = get_object_or_404(Cause, pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        card_number = request.POST.get('card_number', '')
        message_text = request.POST.get('message', '')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, 'Invalid amount.')
            return render(request, 'core/donate.html', {'cause': cause})

        # Simulate payment gateway: fail if card starts with 0000
        if card_number.startswith('0000'):
            messages.error(request, 'Payment failed. Card declined.')
            Donation.objects.create(
                donor=request.user,
                cause=cause,
                amount=amount,
                status='failed',
                transaction_id=str(uuid.uuid4()),
                message=message_text,
            )
            return render(request, 'core/donate.html', {'cause': cause})

        with transaction.atomic():
            donation = Donation.objects.create(
                donor=request.user,
                cause=cause,
                amount=amount,
                status='completed',
                transaction_id=str(uuid.uuid4()),
                message=message_text,
            )
            cause.raised_amount += donation.amount
            cause.save()

            profile, _ = DonorProfile.objects.get_or_create(user=request.user)
            profile.total_donated += donation.amount
            profile.save()

        messages.success(request, f'Donation of ${amount:.2f} to "{cause.title}" successful!')
        return redirect('profile')

    return render(request, 'core/donate.html', {'cause': cause})


@login_required
def profile(request):
    profile, _ = DonorProfile.objects.get_or_create(user=request.user)
    donations = Donation.objects.filter(donor=request.user).order_by('-donated_at')
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'core/profile.html', {'profile': profile, 'donations': donations})


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            DonorProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')
