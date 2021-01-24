from django.urls import path

from . import views

app_name = "ecommerce"

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('dashboard/main/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/products/all/', views.DashboardProductsListView.as_view(), name='dashboard-products'),

    path('dashboard/sales/all/', views.DashboardSalesListView.as_view(), name='dashboard-sales'),
    path('dashboard/sales/all/export/', views.DashboardSalesListView.as_view(), name='dashboard-sales-export'),
    path('dashboard/sales/<int:pk>/update/status/', views.DashBoardUpdateSaleStatus.as_view(),
         name='dashboard-sales-update-status'),

    path('dashboard/index-content/<int:pk>/update/', views.UpdateIndexContent.as_view(),
         name='dashboard-update-index-content'),

    path('about/', views.Index.as_view(), name='about'),
    path('contact/', views.Index.as_view(), name='contact'),

    path('products/list/', views.ProductsListView.as_view(), name='products-list'),
    path('products/list/export/', views.export_products_excel, name='products-list-export'),
    path('products/details/<int:pk>/', views.ViewProductDetailsView.as_view(), name='products-product-details'),
    path('products/create/', views.CreateProduct.as_view(), name='products-product-create'),
    path('products/<int:pk>/update/', views.UpdateProduct.as_view(), name='products-product-update'),
    path('products/<int:pk>/delete/', views.DeleteProduct.as_view(), name='products-product-delete'),

    path('categories/list/', views.CategoriesListView.as_view(), name='categories-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='categories-create'),
    path('categories/sub-categories/create/', views.SubCategoryCreateView.as_view(), name='categories-sub-create'),

    path('cart/add/', views.CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', views.CartRemoveView.as_view(), name='cart-remove'),
    path('cart/details/', views.RedirectToCartDetailsView.as_view(), name='cart-details-redirect'),
    path('cart/details/<int:pk>/', views.CartDetailsView.as_view(), name='cart-details'),
    path('cart/checkout/', views.CartCashOutToOrder.as_view(), name='cart-check-out'),
    path('cart/checkout/confirm/', views.CartCheckOutConfirm.as_view(), name='cart-check-out-confirm'),
    path('cart/get-count/', views.get_cart_count, name='cart-get-count'),

    path('orders/history/', views.OrdersHistory.as_view(), name='orders-history'),
    path('orders/history/export/', views.export_orders_excel, name='orders-history-export'),
    path('orders/change-history/', views.OrdersChangeHistory.as_view(), name='orders-change-history'),
    path('orders/create/', views.OrderCreateView.as_view(), name='orders-create'),
    path('orders/<int:pk>/checkout/', views.OrderCheckOut.as_view(), name='order-check-out'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='orders-order-update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='orders-order-delete'),
    path('orders/<int:pk>/details/', views.OrderDetails.as_view(), name='orders-order-details'),
    path('sales/<int:pk>/details/', views.DashboardSaleDetails.as_view(), name='sales-sale-details'),
    path('orders/lines/<int:pk>/update/', views.OrderLineUpdateView.as_view(), name='orderlines-line-details'),
    path('orders/lines/<int:pk>/delete/', views.OrderLineDeleteView.as_view(), name='orderlines-line-delete'),

    path('favorite/add/', views.FavoriteCreateView.as_view(), name='favorite-add'),
    path('favorite/list/', views.FavoriteListView.as_view(), name='favorite-list'),

    path('reviews/add/', views.FavoriteListView.as_view(), name='review-add'),
]
