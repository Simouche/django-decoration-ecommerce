import xlwt
from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView, ListView, RedirectView

from accounts.forms import LoginForm, RegistrationForm, CreateStaffForm
from accounts.models import Profile, User, State, City
from base_backend import _
from base_backend.decorators import super_user_required
from base_backend.utils import is_ajax


# Create your views here.

class RegisterView(FormView):
    template_name = "register.html"
    success_url = reverse_lazy("accounts:login")
    form_class = RegistrationForm
    initial = {'user_type': 'C'}

    def get_success_url(self):
        if self.request.GET.get('next'):
            self.success_url = self.request.GET.get('next')
            return super(RegisterView, self).get_success_url()
        else:
            return super(RegisterView, self).get_success_url()

    def form_valid(self, form):
        form.save()
        user = authenticate(self.request, username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password'))
        login(self.request, user)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        next = self.request.GET.get('next')
        return super(RegisterView, self).get_context_data(next=next, **kwargs)


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('ecommerce:dashboard')
            return redirect('ecommerce:index')

        login_form = LoginForm()
        context = dict(login_form=login_form, next=self.request.GET.get('next'), form=RegistrationForm())
        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('ecommerce:dashboard')
            return redirect('ecommerce:index')

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
                user = User.objects.filter(username=login_form.cleaned_data.get('username'))
                if user.exists():
                    user = user.first()
                    if not user.is_active:
                        login_form.add_error(None, _("Your account isn't activated, an admin will activate it soon."))
                else:
                    login_form.add_error(None, _('Invalid username/password'))
                context = dict(login_form=login_form, next=self.request.GET.get('next'))
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
    template_name = "dashboard/profile.html"

    def get_queryset(self):
        if not self.request.user.is_staff:
            self.queryset = self.queryset.filter(user=self.request.user)
        return super(ProfileDetailsView, self).get_queryset()


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ['photo', 'address', 'city', 'birth_date', 'gender']
    template_name = "profile.html"
    success_url = "accounts:profile-update"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        context['orders'] = self.request.user.profile.orders.filter(visible=True)
        return context

    def get_success_url(self):
        return reverse_lazy(self.success_url, kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


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
    paginate_by = 10
    allow_empty = True
    ordering = ['-date_joined']

    def get_queryset(self):
        User.objects.filter()
        queryset = super(UserListView, self).get_queryset()
        if self.request.user.user_type == 'S':
            queryset = queryset.filter(user_type__in=['C', 'S'])
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
                                             {'users': context.pop('users', None),
                                              'page_obj': context.pop('page_obj', None)},
                                             request=request)
            return JsonResponse(data)
        else:
            return super(UserListView, self).get(request, *args, **kwargs)


@super_user_required()
def export_users_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('products')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [gettext('First Name'), gettext('Last Name'), gettext('Email'), gettext('phone')]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = User.objects.filter(visible=True).values_list('first_name', 'last_name', 'email', 'phones')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


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


@method_decorator(login_required, name="dispatch")
class StatesList(ListView):
    template_name = "dashboard/states.html"
    model = State
    context_object_name = "states"
    paginate_by = 50


@method_decorator(login_required, name="dispatch")
class CitiesList(ListView):
    template_name = "dashboard/cities.html"
    model = City
    context_object_name = "cities"
    paginate_by = 25
