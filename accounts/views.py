from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView, ListView, RedirectView

from accounts.forms import LoginForm, RegistrationForm, CreateStaffForm
from accounts.models import Profile, User
from base_backend import _
from base_backend.decorators import super_user_required
from base_backend.utils import is_ajax


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
            if request.user.is_staff:
                return redirect('ecommerce:dashboard')
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
                if request.user.is_superuser:
                    return redirect('ecommerce:dashboard')
                if request.user.is_staff:
                    return redirect('ecommerce:dashboard-products')
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
class UserDeleteView(RedirectView):
    permanent = True
    pattern_name = "accounts:users-list"

    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        user.delete()
        return reverse("accounts:users-list")


@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = "dashboard/users.html"
    queryset = User.objects.all()
    context_object_name = 'users'
    extra_context = {'groups': Group.objects.all()}
    page_kwarg = 'page'
    paginate_by = 25
    allow_empty = True
    ordering = ['-date_joined']

    def get_queryset(self):
        User.objects.filter()
        queryset = super(UserListView, self).get_queryset()
        if self.request.GET.get('group', None):
            group = get_object_or_404(Group, id=self.request.GET.get('group', None))
            queryset = queryset.filter(
                groups__in=[group])
        return queryset

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(UserListView, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['users'] = render_to_string('dashboard/_users_table.html',
                                             {'users': context.pop('users', None)},
                                             request=request)
            return JsonResponse(data)
        else:
            return super(UserListView, self).get(request, *args, **kwargs)


@method_decorator(super_user_required, name='dispatch')
class CreateUser(BSModalCreateView):
    model = User
    context_object_name = 'user'
    success_url = reverse_lazy("accounts:users-list")
    template_name = "dashboard/create_user.html"
    success_message = _('User Created Success')
    form_class = CreateStaffForm
    initial = {'user_type': 'S'}


@staff_member_required()
def activate_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    return redirect('accounts:users-list')


@staff_member_required()
def deactivate_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    return redirect('accounts:users-list')


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
