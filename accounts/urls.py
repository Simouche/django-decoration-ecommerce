from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LoginView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profiles/<int:pk>/details/', views.ProfileDetailsView.as_view(), name='profile-details'),
    path('profiles/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile-details'),
    path('users/list/', views.UserListView.as_view(), name='users-list'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='users-delete'),
]
