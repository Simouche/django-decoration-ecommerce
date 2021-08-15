from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('forgot-password/', views.ForgotPassword.as_view(), name='forgot-password'),

    path('profiles/<int:pk>/details/', views.ProfileDetailsView.as_view(), name='profile-details'),
    path('profiles/create/', views.CreateUser.as_view(), name='profile-create'),
    path('profiles/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile-update'),

    path('users/list/', views.UserListView.as_view(), name='users-list'),
    path('users/list/export/', views.export_users_excel, name='users-list-export'),
    path('users/<int:pk>/activate/', views.activate_user, name='users-activate-user'),
    path('users/<int:pk>/deactivate/', views.deactivate_user, name='users-deactivate-user'),
    path('users/change-password/', views.reset_user_password, name='users-change-password'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='users-delete'),

    path('dashboard/places/states/', views.StatesList.as_view(), name="dashboard-states"),
    path('dashboard/places/cities/', views.CitiesList.as_view(), name="dashboard-cities"),
]
