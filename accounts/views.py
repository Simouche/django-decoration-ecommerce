from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView

from accounts.forms import LoginForm, RegistrationForm
from base_backend import _


# Create your views here.


class RegisterView(FormView):
    template_name = ""
    success_url = "accounts:login"
    form_class = RegistrationForm
    initial = {'user_type': 'C'}

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class Login(View):
    template_name = ""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('restaurants:home')  # todo redirect to the index page

        login_form = LoginForm()
        context = dict(login_form=login_form)
        return render(request, self.template_name, context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(username=login_form.cleaned_data.get('username'),
                                password=login_form.cleaned_data.get('password'))
            if user:
                login(request, user)
                if request.GET.get('next', None):
                    return redirect(request.GET.get('next'))
                return redirect('restaurants:home')
            else:
                login_form.add_error(None, _('Invalid username/password'))
                context = dict(login_form=login_form)
                return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('restaurants:home')


class Profile(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


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
