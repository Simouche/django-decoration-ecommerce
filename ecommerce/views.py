from django.shortcuts import render

from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView


# Create your views here.

class DashBoard(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class Index(View):
    def get(self, request):
        pass


class ViewProduct(View):
    def get(self, request):
        pass


class CreateProduct(CreateView):
    pass


class UpdateProduct(UpdateView):
    pass


class DeleteProduct(DeleteView):
    pass


class AddToCart(View):
    pass


class OrdersHistory(ListView):
    pass


class CreateOrder(CreateView):
    pass


class UpdateOrder(UpdateView):
    pass


class DeleteOrder(DeleteView):
    pass


class OrderDetails(DetailView):
    pass
