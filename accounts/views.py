from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView, DeleteView, ListView

from accounts.forms import LoginForm, RegistrationForm
from accounts.models import Profile, User
from base_backend import _


# Create your views here.


class RegisterView(FormView):
    template_name = "register.html"
    success_url = reverse_lazy("accounts:login")
    form_class = RegistrationForm
    initial = {'user_type': 'C'}

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        return context
    
    def form_invalid(self, form):
        print(form.errors)
        return super(RegisterView, self).form_invalid(form)

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('ecommerce:index')

        login_form = LoginForm()
        context = dict(login_form=login_form)
        return render(request, self.template_name, context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, username=login_form.cleaned_data.get('username'),
                                password=login_form.cleaned_data.get('password'))
            if user:
                login(request, user)
                if request.GET.get('next', None):
                    return redirect(request.GET.get('next'))
                return redirect('ecommerce:index')
            else:
                login_form.add_error(None, _('Invalid username/password'))
                context = dict(login_form=login_form)
                return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('ecommerce:index')


@method_decorator(login_required, name='dispatch')
class ProfileDetailsView(DetailView):
    model = Profile
    context_object_name = 'profile'
    queryset = Profile.objects.filter(visible=True)
    template_name = ""

    def get_queryset(self):
        self.queryset = self.queryset.filter(user=self.request.user)
        return super(ProfileDetailsView, self).get_queryset()


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ['photo', 'address', 'city', 'birth_date', 'gender']
    template_name = ""
    success_url = ""


@method_decorator(staff_member_required, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    template_name = ""
    success_url = ""


@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = "dashboard/users.html"
    queryset = User.objects.all()
    context_object_name = 'users'


class ForgotPassword(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class PasswordReset(View):
    def get(self, request):
        pass

    def post(self, request):
        pass
