from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('savita_dashboard/', views.savita_dashboard, name='savita_dashboard'),
    path('rooms/', views.available_rooms, name='available_rooms'),
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('booking/', views.home, name='booking'),

    # Dashboard
    path('room_list/', views.room_list, name='room_list'),
    path('rooms/add/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/edit/', views.room_update, name='room_update'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),

    # Guest URLs
    path('guests/', views.guest_list, name='guest_list'),
    path('guests/add/', views.guest_create, name='guest_create'),
    path('guests/<int:pk>/edit/', views.guest_update, name='guest_update'),
    path('guests/<int:pk>/delete/', views.guest_delete, name='guest_delete'),

    # Booking URLs
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/add/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/edit/', views.booking_update, name='booking_update'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
]

