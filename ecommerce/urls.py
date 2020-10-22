from django.urls import path

from . import views

app_name = "ecommerce"

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('dashboard/main/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/products/all/', views.DashboardProductsListView.as_view(), name='dashboard-products'),
    path('about/', views.Index.as_view(), name='about'),
    path('contact/', views.Index.as_view(), name='contact'),
    path('products/list/', views.ProductsListView.as_view(), name='products-list'),
    path('products/details/<int:pk>/', views.ViewProductDetailsView.as_view(), name='products-product-details'),
    path('products/create/', views.CreateProduct.as_view(), name='products-product-create'),
    path('products/<int:pk>/update/', views.UpdateProduct.as_view(), name='products-product-update'),
    path('products/<int:pk>/delete/', views.DeleteProduct.as_view(), name='products-product-delete'),
    path('cart/add/', views.CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', views.CartRemoveView.as_view(), name='cart-remove'),
    path('cart/details/', views.RedirectToCartDetailsView.as_view(), name='cart-details-redirect'),
    path('cart/details/<int:pk>/', views.CartDetailsView.as_view(), name='cart-details'),
    path('cart/cashout/', views.CartCashOutToOrder.as_view(), name='cart-cash-out'),
    path('cart/get-count/', views.get_cart_count, name='cart-cash-out'),
    path('orders/history/', views.OrdersHistory.as_view(), name='orders-history'),
    path('orders/create/', views.OrderCreateView.as_view(), name='orders-create'),
    path('cart/cashout/', views.CartCashOutToOrder.as_view(), name='cart-cash-out'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='orders-order-update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='orders-order-delete'),
    path('orders/<int:pk>/details/', views.OrderDetails.as_view(), name='orders-order-details'),
    path('orders/lines/<int:pk>/update/', views.OrderLineUpdateView.as_view(), name='orderlines-line-details'),
    path('orders/lines/<int:pk>/delete/', views.OrderLineDeleteView.as_view(), name='orderlines-line-delete'),
    path('favorite/add/', views.FavoriteCreateView.as_view(), name='favorite-add'),
    path('favorite/list/', views.FavoriteListView.as_view(), name='favorite-list'),
    path('reviews/add/', views.FavoriteListView.as_view(), name='review-add'),
]
