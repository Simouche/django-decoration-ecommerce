import csv
import decimal
import json
import random
from django.utils import timezone

import xlwt
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.db.models import Sum, F, Count, QuerySet, Q
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, FormView, TemplateView, \
    RedirectView

from accounts.models import User, State, City
from base_backend import _
from base_backend.decorators import super_user_required
from base_backend.utils import get_current_week, is_ajax, handle_uploaded_file
from decoration.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from ecommerce import current_week_range
from ecommerce.forms import CreateOrderLineForm, CreateProductForm, CreateCategoryForm, CreateSubCategoryForm, \
    SearchOrderStatusChangeHistory, IndexContentForm, CompanyFeesFormset, CreateDeliveryGuyForm, CreateOrderForm, \
    OrderWithLinesFormSet, CartWithLinesFormSet, CartLineForm, CheckoutForm, OrderFilter
from ecommerce.models import Product, Order, OrderLine, Favorite, Cart, CartLine, Category, SubCategory, \
    OrderStatusChange, IndexContent, DeliveryGuy, DeliveryCompany, Deliveries, Rate, Complaint
from ecommerce.reports import render_to_pdf, render_to_pdf2
from django.contrib import messages


class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        m_kwargs = super(Index, self).get_context_data(**kwargs)
        m_kwargs['popular_cats'] = Category.objects.category_with_3_products()[:3]
        m_kwargs['random_products'] = Product.objects.filter(visible=True).order_by('?')[:3]
        m_kwargs['top_pick'] = Product.objects.filter(visible=True).annotate(pick_count=Count('orders_lines')).order_by(
            '-pick_count')[:3]
        m_kwargs["content"] = IndexContent.objects.all().first()
        return m_kwargs


@method_decorator(staff_member_required, name='dispatch')
class Dashboard(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        m_kwargs = super(Dashboard, self).get_context_data(**kwargs)
        order_line_lookup = Q(order__status__in=['CO', 'OD', 'D', 'PA'])
        order_lookup = Q(status__in=['CO', 'OD', 'D', 'PA'])
        m_kwargs["total_users"] = User.objects.filter(user_type="C", is_active=True).count() or 0
        m_kwargs["items_sold"] = OrderLine.objects \
                                     .filter(order_line_lookup) \
                                     .aggregate(count=Sum('quantity')).get('count', 0) or 0
        m_kwargs["items_sold_week"] = OrderLine.objects \
                                          .filter(order_line_lookup, created_at__week=get_current_week()) \
                                          .aggregate(count=Sum('quantity')).get('count', 0) or 0
        m_kwargs["earnings"] = OrderLine.objects \
            .filter(order_line_lookup) \
            .aggregate(earning=Sum(F('quantity') * F('product__price'))).get('earning', 0.0) \
            .quantize(decimal.Decimal("0.01"))
        m_kwargs['total_orders'] = Order.objects.all().count()
        m_kwargs['total_delivered_orders'] = Order.objects.filter(status__in=['D', 'PA']).count()
        m_kwargs['total_canceled_orders'] = Order.objects.filter(status__in=['CA', 'RE', 'R']).count()
        m_kwargs['total_on_delivery_orders'] = Order.objects.filter(status='OD').count()

        m_kwargs['week_orders'] = Order.objects.filter(created_at__range=current_week_range()).count()
        m_kwargs['week_delivered_orders'] = Order.objects.filter(created_at__range=current_week_range(),
                                                                 status__in=['D', 'PA']).count()
        m_kwargs['week_pending_orders'] = Order.objects.filter(created_at__range=current_week_range(),
                                                               status='P').count()
        m_kwargs['week_on_delivery_orders'] = Order.objects.filter(created_at__range=current_week_range(),
                                                                   status='OD').count()

        today = timezone.now()
        m_kwargs['today_orders'] = Order.objects.filter(created_at=today).count()
        m_kwargs['today_delivered_orders'] = Order.objects.filter(created_at=today,
                                                                  status__in=['D', 'PA']).count()
        m_kwargs['today_pending_orders'] = Order.objects.filter(created_at=today,
                                                                status='P').count()
        m_kwargs['today_on_delivery_orders'] = Order.objects.filter(created_at=today,
                                                                    status='OD').count()

        m_kwargs["states"] = Order.objects.filter(order_lookup).values(state_name=F('profile__city__state__name')) \
                                 .annotate(s_count=Count('profile__city__state__name')).order_by('-s_count')[:10]
        m_kwargs["items"] = Product.objects \
                                .values('price', 'stock', product_name=F('name'),
                                        order_count=Count('orders_lines__order'),
                                        quantities=Sum('orders_lines__quantity'), ) \
                                .filter(order_count__gt=0) \
                                .order_by("-order_count")[:10]
        m_kwargs["callers"] = User.objects \
                                  .filter(user_type="CA", orders__status__in=["CO", "OD", "D", "PA"]) \
                                  .annotate(orders_count=Count("orders__id")) \
                                  .order_by("-orders_count")[:10]
        m_kwargs["delivery_guys"] = DeliveryGuy.objects \
                                        .filter(deliveries__order__status__in=["D", "PA"]) \
                                        .annotate(orders_count=Count("deliveries")) \
                                        .order_by("-orders_count")[:10]
        return m_kwargs

    def get(self, request, *args, **kwargs):
        response = super(Dashboard, self).get(request, *args, **kwargs)
        redirect_result = self.redirect()
        if redirect_result is not None:
            return redirect_result
        return response

    def redirect(self):
        if self.request.user.user_type == 'S':
            return redirect("ecommerce:dashboard-products")
        elif self.request.user.user_type == 'CA':
            return redirect("ecommerce:orders-history")


@method_decorator(staff_member_required(), name='dispatch')
class DashboardProductsListView(ListView):
    template_name = "dashboard/products_list.html"
    queryset = Product.objects.all()
    model = Product
    context_object_name = "products"
    page_kwarg = 'page'
    paginate_by = 10
    allow_empty = True
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super(DashboardProductsListView, self).get_queryset()
        if self.request.GET.get('category', None):
            queryset = queryset.filter(
                category__category_id=self.request.GET.get('category', None))
        if self.request.GET.get('sub_category', None):
            queryset = queryset.filter(
                category_id=self.request.GET.get('sub_category', None))
        return queryset

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(DashboardProductsListView, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['products'] = render_to_string('dashboard/_products_table.html',
                                                {'products': context.pop('products', None),
                                                 'page_obj': context.pop('page_obj', None)},
                                                request=request)
            return JsonResponse(data)
        else:
            return super(DashboardProductsListView, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        return super(DashboardProductsListView, self) \
            .get_context_data(object_list=object_list,
                              categories_json=json.dumps(Category.objects.with_sub_cats()),
                              categories=Category.objects.filter(visible=True))


@super_user_required()
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow([_('Name'), _('Name Ar'), _('Name Fr'), _('Price'), _('Stock'), _('Category')])

    products = Product.objects.filter(visible=True).values_list('name', 'name_ar', 'name_en', 'price', 'stock',
                                                                'category__name')
    for product in products:
        writer.writerow(product)

    return response


@super_user_required()
def export_products_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="products.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('products')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [gettext('Name'), gettext('Name Ar'), gettext('Name Fr'), gettext('Price'), gettext('Stock'),
               gettext('Category')]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Product.objects.filter(visible=True).values_list('name', 'name_ar', 'name_en', 'price', 'stock',
                                                            'category__name')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@method_decorator(staff_member_required(), name='dispatch')
class DashboardSalesListView(ListView):
    template_name = "dashboard/sales_list.html"
    queryset = Order.objects.filter(status__in=['CO', 'OD', 'D', 'R', 'RE', 'PA'], visible=True)
    model = Order
    context_object_name = "sales"
    page_kwarg = 'page'
    paginate_by = 50
    allow_empty = True
    ordering = ['-created_at']
    extra_context = {
        "states": State.objects.all(),
        "cities": City.objects.all(),
    }

    def filter_queryset(self, queryset) -> QuerySet:
        self.form = OrderFilter(self.request.GET)
        if self.form.is_valid():
            cd = self.form.cleaned_data
            if cd.get('order'):
                queryset = queryset.filter(pk=cd.get('order').pk)
            if cd.get('user'):
                queryset = queryset.filter(profile__user=cd.get('user'))
            if cd.get('delivery_man'):
                queryset = queryset.filter(deliveries__delivery_guys=cd.get('delivery_man'))
            if cd.get('caller'):
                queryset = queryset.filter(assigned_to=cd.get('caller'))
            if cd.get('start_date'):
                queryset = queryset.filter(created_at__gte=cd.get('start_date'))
            if cd.get('end_date'):
                queryset = queryset.filter(created_at__lte=cd.get('end_date'))
            if cd.get('status'):
                queryset = queryset.filter(status=cd.get('status'))
            return queryset
        else:
            return queryset

    def get_queryset(self):
        queryset = super(DashboardSalesListView, self).get_queryset()
        queryset = self.filter_queryset(queryset)
        if self.request.user.user_type in ['CA', 'S']:
            queryset = queryset.filter(assigned_to=self.request.user)
        if self.request.GET.get('status', None):
            queryset = queryset.filter(status=self.request.GET.get('status', None))
        if self.request.GET.get('city', None):
            queryset = queryset.filter(profile__city=self.request.GET.get('city'))
        if self.request.GET.get('state', None):
            queryset = queryset.filter(profile__city__state=self.request.GET.get('state'))

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        agents = DeliveryGuy.objects.all()

        return super(DashboardSalesListView, self).get_context_data(agents=agents, form=self.form, **kwargs)

    def get(self, request, *args, **kwargs):
        self.form = OrderFilter()
        if is_ajax(request):
            super(DashboardSalesListView, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['sales'] = render_to_string('dashboard/_sales_table.html',
                                             {'sales': context.pop('sales', None),
                                              'page_obj': context.pop('page_obj', None)},
                                             request=request)
            return JsonResponse(data)
        else:
            return super(DashboardSalesListView, self).get(request, *args, **kwargs)


@super_user_required()
def export_sales_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sales')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [gettext('Number'), gettext('Client'), gettext('Phone'), gettext('Items Count'),
               gettext('Status')]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Order.objects.filter(status__in=['CO', 'OD', 'D'], visible=True).annotate(count=Sum('lines__quantity')) \
        .values_list('number', 'profile__user__first_name', 'profile__user__phones',
                     'count', 'status')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@method_decorator(staff_member_required(), name='dispatch')
class DashBoardUpdateSaleStatus(RedirectView):
    pattern_name = "ecommerce:dashboard-sales"

    def get_redirect_url(self, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        order.progress_status()
        if self.request.user.user_type == 'CA':
            return reverse("ecommerce:orders-history")
        return reverse("ecommerce:dashboard-sales")


@method_decorator(staff_member_required(), name='dispatch')
class DashboardSaleDetails(DetailView):
    model = Order
    context_object_name = 'order'
    queryset = Order.objects.filter(status__in=['CO', 'OD', 'D'])
    template_name = "order_details.html"

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(DashboardSaleDetails, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['order'] = render_to_string('dashboard/_order_details.html',
                                             {'order': context.pop('order', None)},
                                             request=request)
            return JsonResponse(data)
        return super(DashboardSaleDetails, self).get(request=request, *args, **kwargs)


class ViewProductDetailsView(DetailView):
    model = Product
    context_object_name = 'product'
    queryset = Product.objects.filter(visible=True)
    template_name = "product_details.html"

    def get_context_data(self, **kwargs):
        m_context = super(ViewProductDetailsView, self).get_context_data(**kwargs)
        product = kwargs.get('product', kwargs.get('object', None))
        if product and self.request.user.is_authenticated:
            m_context['is_favorite'] = product.id in self.request.user.profile.favorites.all().values_list('product',
                                                                                                           flat=True)
        return m_context


class ProductsListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(visible=True)
    template_name = "products.html"
    paginate_by = 12
    page_kwarg = 'page'
    paginate_orphans = True
    ordering = ['-created_at']


@method_decorator(staff_member_required, name='dispatch')
class CreateProduct(BSModalCreateView):
    model = Product
    context_object_name = 'product'
    success_url = reverse_lazy("ecommerce:dashboard-products")
    template_name = "dashboard/create_product.html"
    success_message = _("Product Created Successfully")
    form_class = CreateProductForm

    def form_valid(self, form):
        if self.request.POST.get('asyncUpdate', None):
            response = super(CreateProduct, self).form_valid(form=form)
            images = self.request.FILES.getlist('media')
            for image in images:
                path = MEDIA_ROOT + '/products/' + image.name
                url = MEDIA_URL + 'products/' + image.name
                handle_uploaded_file(image, path)
                self.object.slider.append(url)
            self.object.save()
            return response
        return super(CreateProduct, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class UpdateProduct(BSModalUpdateView):
    model = Product
    context_object_name = 'product'
    form_class = CreateProductForm
    success_url = reverse_lazy("ecommerce:dashboard-products")
    template_name = "dashboard/create_product.html"
    queryset = Product.objects.filter(visible=True)


@method_decorator(staff_member_required, name='dispatch')
class DeleteProduct(RedirectView):
    permanent = True
    pattern_name = "ecommerce:dashboard-products"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs['pk'])
        product.delete()
        return reverse("ecommerce:dashboard-products")


# cart
class CartMixin:
    def my_get_queryset(self, queryset):
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(profile=self.request.user.profile)


@method_decorator(login_required, name='dispatch')
class RedirectToCartDetailsView(RedirectView):
    permanent = True
    pattern_name = 'ecommerce:cart-details'

    def get_redirect_url(self, *args, **kwargs):
        url = reverse(self.pattern_name, kwargs={'pk': self.request.user.profile.cart.id})
        return url


@method_decorator(login_required, name='dispatch')
class CartDetailsView(DetailView, CartMixin):
    model = Cart
    template_name = "cart.html"
    context_object_name = "cart"
    queryset = Cart.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(CartDetailsView, self).get_queryset()
        return self.my_get_queryset(queryset)

    def get_context_data(self, **kwargs):
        return super(CartDetailsView, self).get_context_data(cart_lines=self.get_form(), **kwargs)

    def get_form(self):
        cart_lines = CartWithLinesFormSet(instance=self.object)
        return cart_lines


@method_decorator(login_required, name='dispatch')
class CartAddView(CreateView):
    model = CartLine
    context_object_name = "cart_line"
    fields = ['product', 'cart', 'quantity']
    template_name = "index.html"
    success_url = reverse_lazy('ecommerce:index')

    def get_initial(self):
        initials = super(CartAddView, self).get_initial()
        initials['cart'] = self.request.user.profile.cart
        return initials

    def form_invalid(self, form):
        return super(CartAddView, self).form_invalid(form=form)

    def form_valid(self, form):
        if self.request.is_ajax():
            super(CartAddView, self).form_valid(form=form)
            return JsonResponse({'status': 'Success'})
        else:
            return super(CartAddView, self).form_valid(form=form)


@method_decorator(login_required, name='dispatch')
class CartUpdateView(FormView):
    template_name = "cart.html"
    form_class = CartWithLinesFormSet

    def get_queryset(self):
        return self.request.user.profile.cart.get_lines

    def get_object(self):
        return self.request.user.profile.cart

    def get_form_kwargs(self):
        kwargs = super(CartUpdateView, self).get_form_kwargs()
        kwargs['instance'] = self.get_object()
        if self.request.method in ['POST', 'PUT']:
            kwargs['form_kwargs'] = dict(editable=True)
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(CartUpdateView, self).form_valid(form)

    def get_success_url(self):
        self.success_url = reverse_lazy("ecommerce:cart-details", kwargs={"pk": self.request.user.profile.cart.id})
        return super(CartUpdateView, self).get_success_url()

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class CartRemoveView(DeleteView):
    model = CartLine
    template_name = ""
    context_object_name = "cart_line"


@method_decorator(login_required, name='dispatch')
class CartCashOutToOrder(TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        form = CheckoutForm(initial=self.get_initial())
        return super(CartCashOutToOrder, self).get_context_data(form=form, **kwargs)

    def get_initial(self) -> dict:
        first_name = self.request.user.first_name
        last_name = self.request.user.last_name
        phone_number = self.request.user.phones[0]
        email_address = self.request.user.email
        city = self.request.user.profile.city
        address = self.request.user.profile.address
        initials = dict(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email_address=email_address,
            city=city,
            address=address,
        )
        return initials


@method_decorator(login_required, name='dispatch')
class CartCheckOutConfirm(RedirectView):
    pattern_name = "ecommerce:order-check-out"
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        if form.is_valid():
            form.save(self.request.user)
            order = self.request.user.profile.cart.confirm(note=form.cleaned_data.get('note'))
            url = reverse(self.pattern_name, kwargs={'pk': order.id})
            return url
        url = reverse("ecommerce:cart-check-out")
        return url


# orders and order lines
class OrdersMixin:
    def my_get_queryset(self, queryset):
        if self.request.user.is_staff:
            queryset = queryset.filter(status__in=['P', 'CA', 'RC', 'NA'])
            if self.request.user.user_type in ['CA', 'S']:
                queryset = queryset.filter(assigned_to=self.request.user)
            return queryset
        return queryset.filter(profile=self.request.user.profile)


@method_decorator(login_required, name='dispatch')
class OrdersHistory(ListView, OrdersMixin):
    ordering = "-created_at"
    queryset = Order.objects.filter(visible=True)
    context_object_name = "orders"
    paginate_by = 10
    paginate_orphans = True
    allow_empty = True
    extra_context = {
        "states": State.objects.all(),
        "cities": City.objects.all(),
    }

    def get_template_names(self):
        names = []
        if self.request.user.is_staff:
            names.append("dashboard/orders_list.html")
        else:
            names.append("orders_list.html")
        return names

    def get_queryset(self):
        queryset = super(OrdersHistory, self).get_queryset()
        if self.request.GET.get('status', None):
            queryset = queryset.filter(status=self.request.GET.get('status', None))
        if self.request.GET.get('state', None):
            queryset = queryset.filter(profile__city__state=self.request.GET.get('state'))
        if self.request.GET.get('city', None):
            queryset = queryset.filter(profile__city=self.request.GET.get('city'))
        return self.my_get_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super(OrdersHistory, self).get_context_data(**kwargs)
        total = 0
        if kwargs.get('object_list'):
            for order in kwargs.get('object_list'):
                total += order.sub_total
        context['total'] = total
        context['callers'] = User.objects.filter(user_type='CA')
        return context

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(OrdersHistory, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['orders'] = render_to_string('dashboard/_orders_table.html',
                                              {'orders': context.pop('orders', None),
                                               'page_obj': context.pop('page_obj', None)},
                                              request=request)
            return JsonResponse(data)
        else:
            return super(OrdersHistory, self).get(request, *args, **kwargs)


@super_user_required()
def export_orders_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="orders.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('orders')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [gettext('Number'), gettext('Client'), gettext('Phone'), gettext('Items Count'),
               gettext('Status')]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Order.objects.filter(visible=True).annotate(count=Sum('lines__quantity')) \
        .values_list('number', 'profile__user__first_name', 'profile__user__phones',
                     'count', 'status')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@method_decorator(super_user_required, name='dispatch')
class OrdersChangeHistory(ListView):
    ordering = "-created_at"
    queryset = OrderStatusChange.objects.all()
    context_object_name = "status_changes"
    template_name = "dashboard/order_change_history_list.html"
    paginate_by = 20
    paginate_orphans = True
    allow_empty = True

    def filter_queryset(self, queryset) -> QuerySet:
        self.search_form = SearchOrderStatusChangeHistory(self.request.GET)
        if self.search_form.is_valid():
            if self.search_form.cleaned_data.get('date'):
                queryset = queryset.filter(created_at__date=self.search_form.cleaned_data.get('date'))
            if self.search_form.cleaned_data.get('time'):
                queryset = queryset.filter(created_at__time__gte=self.search_form.cleaned_data.get('time'))
            if self.search_form.cleaned_data.get('user'):
                queryset = queryset.filter(user=self.search_form.cleaned_data.get('user'))
            if self.search_form.cleaned_data.get('order'):
                queryset = queryset.filter(order=self.search_form.cleaned_data.get('order'))
            if self.search_form.cleaned_data.get('from_status'):
                queryset = queryset.filter(previous_status=self.search_form.cleaned_data.get('from_status'))
            if self.search_form.cleaned_data.get('to_status'):
                queryset = queryset.filter(new_status=self.search_form.cleaned_data.get('to_status'))
            return queryset
        else:
            return queryset

    def get_queryset(self):
        queryset = super(OrdersChangeHistory, self).get_queryset()
        return self.filter_queryset(queryset)

    def get_context_data(self, *, object_list=None, **kwargs):
        users = User.objects.all()
        return super(OrdersChangeHistory, self).get_context_data(object_list=object_list, users=users,
                                                                 form=self.search_form)

    def get(self, request, *args, **kwargs):
        self.search_form = SearchOrderStatusChangeHistory()
        return super(OrdersChangeHistory, self).get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class OrderCreateView(FormView):
    model = Order
    context_object_name = 'order'
    form_class = formset_factory(CreateOrderLineForm, extra=1, min_num=1, validate_min=True)
    success_url = ""
    template_name = ""

    def get_initial(self):
        initials = super(OrderCreateView, self).get_initial()
        initials['profile'] = self.request.user.profile
        return initials

    def form_valid(self, forms):
        order = Order.objects.create(number=Order.generate_number(), profile=self.request.user.profile)

        def assign_order_to_line(line_form):
            line_form.order = order
            line_form.save()

        map(assign_order_to_line, forms)
        return HttpResponseRedirect(self.get_success_url(), pk=order.pk)


@method_decorator(login_required, name='dispatch')
class OrderUpdateView(UpdateView, OrdersMixin):
    model = Order
    context_object_name = 'order'
    success_url = reverse_lazy("ecommerce:orders-history")
    template_name = "dashboard/update_order.html"
    queryset = Order.objects.filter(visible=True)
    form_class = CreateOrderForm

    def get_context_data(self, **kwargs):
        data = super(OrderUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['lines_form'] = OrderWithLinesFormSet(self.request.POST, instance=self.object)
        else:
            form = OrderWithLinesFormSet(instance=self.object)
            data['lines_form'] = form
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lines_form = context['lines_form']
        with transaction.atomic():
            self.object = form.save()
            if lines_form.is_valid():
                lines_form.instance = self.object
                lines_form.save()
        return super(OrderUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(OrderUpdateView, self).get_form_kwargs()
        is_caller = self.request.user.user_type == 'CA'
        kwargs['is_caller'] = is_caller
        return kwargs

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(OrderUpdateView, self).get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class OrderDeleteView(DeleteView, OrdersMixin):
    model = Order
    template_name = ""
    success_url = ""
    queryset = Order.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderDeleteView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
class OrderDetails(DetailView, OrdersMixin):
    model = Order
    context_object_name = 'order'
    queryset = Order.objects.filter(visible=True)
    template_name = "order_details.html"

    def get_queryset(self):
        queryset = super(OrderDetails, self).get_queryset()
        return self.my_get_queryset(queryset)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(OrderDetails, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['order'] = render_to_string('dashboard/_order_details.html',
                                             {'order': context.pop('order', None)},
                                             request=request)
            return JsonResponse(data)
        return super(OrderDetails, self).get(request=request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class OrderCheckOut(DetailView):
    model = Order
    context_object_name = 'order'
    queryset = Order.objects.filter(visible=True)
    template_name = "order_confirmed.html"


class OrderLineMixin:
    def my_get_queryset(self, queryset):
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(order__profile=self.request.user.profile)


@method_decorator(login_required, name='dispatch')
class OrderLineCreateView(CreateView):
    pass


@method_decorator(login_required, name='dispatch')
class OrderLineUpdateView(UpdateView):
    model = OrderLine
    context_object_name = 'order'
    fields = ['product', 'quantity']
    success_url = ""
    template_name = ""
    queryset = OrderLine.objects.all()

    def get_queryset(self):
        queryset = super(OrderLineUpdateView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
class OrderLineDeleteView(DeleteView):
    model = OrderLine
    context_object_name = 'order'
    success_url = ""
    template_name = ""
    queryset = OrderLine.objects.filter()

    def get_queryset(self):
        queryset = super(OrderLineDeleteView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
class FavoriteCreateView(CreateView):
    model = Favorite
    context_object_name = 'favorite'
    fields = ['product', 'profile']
    template_name = "index.html"
    success_url = reverse_lazy('ecommerce:index')

    def get_initial(self):
        initials = super(FavoriteCreateView, self).get_initial()
        initials['profile'] = self.request.user.profile
        return initials

    def form_valid(self, form):
        if self.request.is_ajax():
            super(FavoriteCreateView, self).form_valid(form=form)
            return JsonResponse({'status': 'Success'})
        else:
            return super(FavoriteCreateView, self).form_valid(form=form)


@method_decorator(login_required, name='dispatch')
class FavoriteListView(ListView):
    model = Favorite
    template_name = ""
    context_object_name = "favorites"
    queryset = Favorite.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(FavoriteListView, self).get_queryset()
        return queryset.filter(profile=self.request.user.profile)


@login_required()
def get_cart_count(request):
    try:
        return JsonResponse({'count': request.user.profile.cart.get_lines.count()})
    except Exception:
        return JsonResponse({'count': 0})


class CategoriesListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(visible=True)
    template_name = "categories.html"
    paginate_by = 21
    page_kwarg = 'page'
    paginate_orphans = True
    extra_context = {'categories': Category.objects.filter(visible=True),
                     'sub_categories': SubCategory.objects.filter(visible=True)}
    allow_empty = True
    ordering = 'pk'

    def search(self):
        queries = self.request.GET
        if queries.get('category', None):
            self.queryset = self.queryset.filter(category__category_id=queries.get('category'))
        if queries.get('sub_category', None):
            self.queryset = self.queryset.filter(category_id=queries.get('sub_category'))
        if queries.get('color', 'any') and not queries.get('color', 'any') == 'any':
            self.queryset = self.queryset.filter(colors__contains=[queries.get('color')])
        if queries.get('from', 0):
            self.queryset = self.queryset.filter(price__gte=queries.get('from', 0))
        if queries.get('to', 0):
            self.queryset = self.queryset.filter(price__lte=queries.get('to', 0))
        if queries.get('period'):
            integer = 0
            # todo implement the cases for this

    def get(self, request, *args, **kwargs):
        self.search()
        return super(CategoriesListView, self).get(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CreateCategoryForm
    template_name = "dashboard/create_category.html"
    success_url = reverse_lazy("ecommerce:dashboard-products")

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = None
            context = self.get_context_data()
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(CategoryCreateView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _('Category created successfully'))
        return super(CategoryCreateView, self).form_valid(form=form)

    def form_invalid(self, form):
        messages.error(self.request, _('Failed to create a new category.'))
        return redirect("ecommerce:dashboard-products")


@method_decorator(staff_member_required, name='dispatch')
class SubCategoryCreateView(CreateView):
    model = SubCategory
    template_name = "dashboard/create_sub_category.html"
    form_class = CreateSubCategoryForm
    success_url = reverse_lazy("ecommerce:dashboard-products")

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = None
            context = self.get_context_data()
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(SubCategoryCreateView, self).get(request, *args, **kwargs)


@method_decorator(permission_required("ecommerce.add_indexcontent"), name='dispatch')
class UpdateIndexContent(UpdateView):
    model = IndexContent
    form_class = IndexContentForm
    template_name = "dashboard/index_content_form.html"
    context_object_name = "index_content"

    def get_success_url(self):
        return reverse_lazy("ecommerce:dashboard-update-index-content", kwargs={"pk": 1})


@method_decorator(staff_member_required, name="dispatch")
class CreateDeliveryGuy(CreateView):
    model = DeliveryGuy
    template_name = "dashboard/create_delivery_guy.html"
    success_url = reverse_lazy("ecommerce:delivery-agents-list")
    form_class = CreateDeliveryGuyForm

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = None
            context = self.get_context_data()
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(CreateDeliveryGuy, self).get(request, *args, **kwargs)


@method_decorator(staff_member_required, name="dispatch")
class DeliveriesView(ListView):
    model = Deliveries
    template_name = "dashboard/deliveries.html"
    queryset = Deliveries.objects.all()
    context_object_name = "deliveries"

    def get_queryset(self):
        queryset = super(DeliveriesView, self).get_queryset()
        queryset = queryset.filter(delivery_guys=self.kwargs.get('pk'))
        return queryset

    def get(self, request, *args, **kwargs):
        super(DeliveriesView, self).get(request, *args, **kwargs)
        context = self.get_context_data()
        data = dict()
        data['deliveries'] = render_to_string(self.template_name,
                                              {'deliveries': context.pop('deliveries', None)},
                                              request=request)
        return JsonResponse(data)


@method_decorator(staff_member_required, name="dispatch")
class UpdateDeliveryGuy(UpdateView):
    template_name = "dashboard/update_delivery_guy.html"
    model = DeliveryGuy
    success_url = reverse_lazy("ecommerce:delivery-agents-list")
    form_class = CreateDeliveryGuyForm

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(UpdateDeliveryGuy, self).get(request, *args, **kwargs)


@method_decorator(staff_member_required, name="dispatch")
class ListDeliveryGuy(ListView):
    model = DeliveryGuy
    template_name = "dashboard/delivery_guys.html"
    queryset = DeliveryGuy.objects.all()
    context_object_name = "guys"
    paginate_by = 25
    ordering = ['-id']


@method_decorator(staff_member_required, name="dispatch")
class CreateDeliveryCompany(CreateView):
    model = DeliveryCompany
    success_url = reverse_lazy("ecommerce:delivery-companies-list")
    template_name = "dashboard/create_company.html"
    fields = ['company_name', 'weight_threshold', 'base_fee']

    def get_context_data(self, **kwargs):
        data = super(CreateDeliveryCompany, self).get_context_data(**kwargs)
        if self.request.POST:
            data['fees_form'] = CompanyFeesFormset(self.request.POST)
        else:
            form = CompanyFeesFormset()
            for i, j in enumerate(form.extra_forms):
                form.forms[i].initial['state'] = i + 49
            data['fees_form'] = form
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fees_form = context['fees_form']
        with transaction.atomic():
            self.object = form.save()
            if fees_form.is_valid():
                fees_form.instance = self.object
                fees_form.save()
        return super(CreateDeliveryCompany, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = None
            context = self.get_context_data()
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(CreateDeliveryCompany, self).get(request, *args, **kwargs)


@method_decorator(staff_member_required, name="dispatch")
class ListDeliveryCompanies(ListView):
    model = DeliveryCompany
    template_name = "dashboard/delivery_companies.html"
    queryset = DeliveryCompany.objects.filter(visible=True)
    context_object_name = "companies"
    paginate_by = 25


@method_decorator(staff_member_required, name="dispatch")
class DetailDeliveryCompany(DetailView):
    model = DeliveryCompany
    context_object_name = "company"
    template_name = "dashboard/company_details.html"
    queryset = DeliveryCompany.objects.filter(visible=True)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            html = render_to_string(self.template_name,
                                    context=context,
                                    request=request)
            return JsonResponse(html, safe=False)
        return super(DetailDeliveryCompany, self).get(request, *args, **kwargs)


@login_required()
def assign_orders_to_caller(request):
    caller = get_object_or_404(User, pk=request.POST.get('caller'), user_type='CA')
    Order.objects.filter(pk__in=request.POST.getlist('orders[]')).update(assigned_to=caller)
    return JsonResponse({"status": 'Success'})


@login_required()
def assign_orders_to_delivery_guy(request):
    ids = request.POST.getlist('orders[]')
    delivery_guy_id = request.POST.get('delivery_guy')
    orders = Order.objects.filter(pk__in=ids)
    delivery_guy = get_object_or_404(DeliveryGuy, pk=delivery_guy_id)
    Deliveries.objects.filter(order__in=orders).delete()
    deliveries = [Deliveries(order=order, delivery_guys=delivery_guy) for order in orders]
    deliveries = Deliveries.objects.bulk_create(deliveries)
    if deliveries:
        orders.update(status='OD')
        total = 0
        for order in orders:
            total += order.total_sum
        context = {
            'orders': orders,
            'delivery_guy': delivery_guy,
            'total': total
        }
        pdf = render_to_pdf2('dashboard/roadmap_pdf_template.html', context)
        response = JsonResponse({"url": pdf})
        return response
    return JsonResponse({"status": 'Fail'})


@method_decorator(login_required, name="dispatch")
class AddReview(CreateView):
    model = Rate
    fields = ['comment', 'product', 'profile']
    template_name = "product_details.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.request.user.profile
        self.object.stars = random.randint(0, 5)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("ecommerce:products-product-details", kwargs={"pk": self.object.product.pk})


@method_decorator(login_required, name="dispatch")
class LoginRequired(RedirectView):
    permanent = True
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        self.url = self.request.GET.get('next')
        return super(LoginRequired, self).get_redirect_url(*args, **kwargs)


@login_required
def print_view(request, order_id):
    if request.method == "GET":
        if order_id is None:
            return JsonResponse({"message": "no order id provided"})

        order = get_object_or_404(Order, pk=order_id)

        pdf = render_to_pdf('dashboard/invoice_pdf_template.html', {'order': order})

        return pdf


@login_required
def get_file(request, file_name):
    if request.method == "GET":
        fss = FileSystemStorage(BASE_DIR / "uploads/invoices")
        file = fss.open(file_name)
        return FileResponse(file, as_attachment=True, filename=file_name)


@method_decorator(login_required, name="dispatch")
class ComplaintsList(ListView):
    model = Complaint
    template_name = "dashboard/complaints.html"
    queryset = Complaint.objects.filter(visible=True)
    paginate_by = 50
    context_object_name = "complaints"
    allow_empty = True

    def get_queryset(self):
        queryset = super(ComplaintsList, self).get_queryset()
        if self.request.GET.get('type', None):
            queryset = queryset.filter(complaint=self.request.GET.get('type', None))
        return queryset

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(ComplaintsList, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['complaints'] = render_to_string('dashboard/_complaints_table.html',
                                                  {'complaints': context.pop('complaints', None),
                                                   'page_obj': context.pop('page_obj', None)},
                                                  request=request)
            return JsonResponse(data)
        else:
            return super(ComplaintsList, self).get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DeliveryManRecapView(TemplateView):
    template_name = "dashboard/delivery_man_recap.html"

    def get_context_data(self, **kwargs):
        delivery_man = get_object_or_404(DeliveryGuy, pk=self.request.GET.get('pk'))
        deliveries = delivery_man.deliveries.filter(order__status__in=['OD'])
        orders = [delivery.order for delivery in deliveries]
        products = {}
        for order in orders:
            for line in order.get_lines:
                product = line.product.name
                if products.get(product, None):
                    products[product] += line.quantity
                else:
                    products[product] = line.quantity

        delivered_deliveries = delivery_man.deliveries.filter(order__status__in=['D'])
        money = 0
        for delivery in delivered_deliveries:
            money += delivery.order.total_sum

        return super(DeliveryManRecapView, self).get_context_data(money=money, products=products,
                                                                  delivery_man=delivery_man, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = dict()
        data['html'] = render_to_string(self.template_name, context, request=request)
        return JsonResponse(data)
