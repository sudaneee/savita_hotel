from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Room, Booking, Guest
from .forms import BookingForm
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import BookingForm


from django.urls import reverse

from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username  # Set session data
            return redirect('savita_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'savita_admin/login.html')


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    request.session.flush()  # Clear all session data
    return redirect('login')


@login_required(login_url='login')
def savita_dashboard(request):
    return render(request, 'savita_admin/dashboard.html')


def available_rooms(request):
    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')
    
    if check_in_date and check_out_date:
        booked_rooms = Booking.objects.filter(
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        ).values_list('room_id', flat=True)
        
        rooms = Room.objects.exclude(id__in=booked_rooms).filter(is_available=True)
    else:
        rooms = Room.objects.filter(is_available=True)
    
    return render(request, 'savita_admin/available_rooms.html', {'rooms': rooms})



def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            guest = form.save()
            booking = Booking(
                room=room,
                guest=guest,
                check_in_date=form.cleaned_data['check_in_date'],
                check_out_date=form.cleaned_data['check_out_date'],
            )
            booking.save()
            room.is_available = False
            room.save()
            return HttpResponse("Booking successful!")
    else:
        form = BookingForm()
    
    return render(request, 'book_room.html', {'form': form, 'room': room})




# View to handle booking form
def home(request):
    if request.method == "POST":
        # Extract data from the form
        email = request.POST.get('email')
        arrival_date = request.POST.get('arrival')
        departure_date = request.POST.get('departure')
        guest_count = request.POST.get('guest')
        room_id = request.POST.get('room')

        # Validate dates
        try:
            arrival_date = datetime.strptime(arrival_date, '%m/%d/%Y').date()
            departure_date = datetime.strptime(departure_date, '%m/%d/%Y').date()

            if arrival_date >= departure_date:
                raise ValidationError("Check-out date must be after check-in date.")
        except ValueError:
            return HttpResponse("Invalid date format. Please use mm/dd/yyyy.", status=400)
        
        # Find the room based on room type
        try:
            room = Room.objects.get(id=room_id, is_available=True)
        except Room.DoesNotExist:
            return HttpResponse("No available room of the selected type.", status=400)

        # Create or retrieve the guest object
        guest, created = Guest.objects.get_or_create(email=email)

        # Create the booking
        try:
            with transaction.atomic():
                booking = Booking.objects.create(
                    room=room,
                    guest=guest,
                    check_in_date=arrival_date,
                    check_out_date=departure_date
                )
                booking.save()
                room.is_available = False  # Update room availability
                room.save()

            # Render booking confirmation template with details
            return render(request, "src/booking_confirmation.html", {
                "booking": booking,
                "room": room,
                "guest": guest,
                "arrival_date": arrival_date,
                "departure_date": departure_date,
                "total_price": booking.total_price
            })

        except Exception as e:
            return HttpResponse(f"Error in booking: {str(e)}", status=500)
    else:
        # GET request: Show the form
        rooms = Room.objects.filter(is_available=True)
        return render(request, "src/index.html", {"rooms": rooms})



# Room Views
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'savita_admin/room_list.html', {'rooms': rooms})



def room_create(request):
    if request.method == 'POST':
        try:
            # Get form data
            room_number = request.POST.get('room_number', '').strip()
            room_type = request.POST.get('room_type', '').strip()
            price_per_night = request.POST.get('price_per_night', '').strip()
            is_available = request.POST.get('is_available') == 'on'  # Properly handle checkbox

            # Validate form data
            if not room_number or not room_type or not price_per_night:
                messages.error(request, 'All fields are required.')
                return render(request, 'savita_admin/room_form.html')

            # Create the Room object
            Room.objects.create(
                room_number=room_number,
                room_type=room_type,
                price_per_night=price_per_night,
                is_available=is_available,
            )
            messages.success(request, 'Room created successfully.')
            return redirect('room_list')

        except Exception as e:
            messages.error(request, f'Error creating room: {str(e)}')

    return render(request, 'savita_admin/room_form.html')


def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        try:
            # Get form data
            room.room_number = request.POST.get('room_number', '').strip()
            room.room_type = request.POST.get('room_type', '').strip()
            room.price_per_night = request.POST.get('price_per_night', '').strip()
            room.is_available = request.POST.get('is_available') == 'on'  # Properly handle checkbox

            # Validate form data
            if not room.room_number or not room.room_type or not room.price_per_night:
                messages.error(request, 'All fields are required.')
                return render(request, 'savita_admin/room_form.html', {'room': room})

            # Save the updated Room object
            room.save()
            messages.success(request, 'Room updated successfully.')
            return redirect('room_list')

        except Exception as e:
            messages.error(request, f'Error updating room: {str(e)}')

    return render(request, 'savita_admin/room_form.html', {'room': room})


def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.delete()
    messages.success(request, 'Room deleted successfully.')
    return redirect('room_list')


# Guest Views
def guest_list(request):
    guests = Guest.objects.all()
    return render(request, 'savita_admin/guest_list.html', {'guests': guests})

def guest_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        Guest.objects.create(name=name, email=email, phone_number=phone_number)
        messages.success(request, 'Guest created successfully.')
        return redirect('guest_list')
    return render(request, 'savita_admin/guest_form.html')

def guest_update(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == 'POST':
        guest.name = request.POST['name']
        guest.email = request.POST['email']
        guest.phone_number = request.POST['phone_number']
        guest.save()
        messages.success(request, 'Guest updated successfully.')
        return redirect('guest_list')
    return render(request, 'savita_admin/guest_form.html', {'guest': guest})

def guest_delete(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    guest.delete()
    messages.success(request, 'Guest deleted successfully.')
    return redirect('guest_list')


# Booking Views
def booking_list(request):
    bookings = Booking.objects.select_related('room', 'guest').all()
    return render(request, 'savita_admin/booking_list.html', {'bookings': bookings})

def booking_create(request):
    rooms = Room.objects.filter(is_available=True)
    guests = Guest.objects.all()
    if request.method == 'POST':
        room_id = request.POST['room']
        guest_id = request.POST['guest']
        check_in_date = request.POST['check_in_date']
        check_out_date = request.POST['check_out_date']
        room = Room.objects.get(id=room_id)
        guest = Guest.objects.get(id=guest_id)
        booking = Booking.objects.create(
            room=room,
            guest=guest,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        room.is_available = False  # Mark room as unavailable
        room.save()
        messages.success(request, 'Booking created successfully.')
        return redirect('booking_list')
    return render(request, 'savita_admin/booking_form.html', {'rooms': rooms, 'guests': guests})

def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    rooms = Room.objects.filter(is_available=True) | Room.objects.filter(id=booking.room.id)
    guests = Guest.objects.all()
    if request.method == 'POST':
        booking.room = Room.objects.get(id=request.POST['room'])
        booking.guest = Guest.objects.get(id=request.POST['guest'])
        booking.check_in_date = request.POST['check_in_date']
        booking.check_out_date = request.POST['check_out_date']
        booking.save()
        messages.success(request, 'Booking updated successfully.')
        return redirect('booking_list')
    return render(request, 'savita_admin/booking_form.html', {'booking': booking, 'rooms': rooms, 'guests': guests})

def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.room.is_available = True  # Mark room as available
    booking.room.save()
    booking.delete()
    messages.success(request, 'Booking deleted successfully.')
    return redirect('booking_list')
