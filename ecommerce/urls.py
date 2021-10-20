from django.urls import path

from . import views

app_name = "ecommerce"

urlpatterns = [

    path('', views.Index.as_view(), name='index'),
    path('dashboard/main/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/products/all/', views.DashboardProductsListView.as_view(), name='dashboard-products'),

    path('dashboard/sales/all/', views.DashboardSalesListView.as_view(), name='dashboard-sales'),
    path('dashboard/coupon/all/', views.CouponListView.as_view(), name='dashboard-coupons'),
    path('dashboard/coupon/create/', views.CreateCoupon.as_view(), name='dashboard-coupons-create'),
    path('dashboard/sales/all/export/', views.DashboardSalesListView.as_view(), name='dashboard-sales-export'),
    path('dashboard/sales/<int:pk>/update/status/', views.DashBoardUpdateSaleStatus.as_view(),
         name='dashboard-sales-update-status'),
    path('dashboard/index-content/<int:pk>/update/', views.UpdateIndexContent.as_view(),
         name='dashboard-update-index-content'),
    path('dashboard/quick-links/create/', views.CreateQuickLink.as_view(),
         name='dashboard-quick-links-create'),
    path('dashboard/partners/create/', views.CreatePartner.as_view(),
         name='dashboard-partners-create'),
    path('dashboard/settings/<int:pk>/update/', views.UpdateSettings.as_view(),
         name='dashboard-update-settings'),
    path('dashboard/print/<int:order_id>/', views.print_view, name='print_order'),
    path('dashboard/print/orders/', views.print_view, name='print_orders'),
    path('dashboard/print/orders/route-sheet/', views.print_route_sheet, name='print_route_sheet'),
    path('dashboard/getfile/<str:file_name>/', views.get_file, name='get_file'),

    path('about/', views.About.as_view(), name='about'),
    path('contact/', views.Contact.as_view(), name='contact'),

    path('products/list/', views.ProductsListView.as_view(), name='products-list'),
    path('products/list/export/', views.export_products_excel, name='products-list-export'),
    path('products/details/<int:pk>/', views.ViewProductDetailsView.as_view(), name='products-product-details'),
    path('products/create/', views.CreateProduct.as_view(), name='products-product-create'),
    path('products/<int:pk>/update/', views.UpdateProduct.as_view(), name='products-product-update'),
    path('products/<int:pk>/delete/', views.DeleteProduct.as_view(), name='products-product-delete'),

    path('categories/list/', views.CategoriesListView.as_view(), name='categories-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='categories-create'),
    path('categories/sub-categories/create/', views.SubCategoryCreateView.as_view(), name='categories-sub-create'),

    path('dashboard/delivery/agents/', views.ListDeliveryGuy.as_view(), name="delivery-agents-list"),
    path('dashboard/delivery/agents/<int:pk>/update/', views.UpdateDeliveryGuy.as_view(),
         name="delivery-agents-update"),
    path('dashboard/delivery/agents/create/', views.CreateDeliveryGuy.as_view(), name="delivery-agents-create"),
    path('dashboard/delivery/agents/show-deliveries/<int:pk>/', views.DeliveriesView.as_view(),
         name="delivery-agents-deliveries"),

    path('dashboard/clients/complaints/list/', views.ComplaintsList.as_view(), name="clients-complaints-list"),

    path('dashboard/delivery/companies/', views.ListDeliveryCompanies.as_view(), name="delivery-companies-list"),
    path('dashboard/delivery/companies/create/', views.CreateDeliveryCompany.as_view(),
         name="delivery-companies-create"),
    path('dashboard/delivery/companies/<int:pk>/', views.DetailDeliveryCompany.as_view(),
         name="delivery-companies-detail"),
    path('dashboard/delivery/companies/<int:pk>/update/', views.UpdateDeliveryCompany.as_view(),
         name="delivery-companies-update"),

    path('dashboard/recap/delivery-man/', views.DeliveryManRecapView.as_view(), name='delivery-man-recap'),
    path('dashboard/recap/product/<int:pk>/', views.product_recap, name='product-recap'),
    path('dashboard/recap/delivery-man/print/', views.print_recap, name='delivery-man-recap-print'),

    path('cart/add/', views.CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', views.CartRemoveView.as_view(), name='cart-remove'),
    path('cart/details/', views.RedirectToCartDetailsView.as_view(), name='cart-details-redirect'),
    path('cart/details/<int:pk>/', views.CartDetailsView.as_view(), name='cart-details'),
    path('cart/update/', views.CartUpdateView.as_view(), name='cart-update'),
    path('cart/checkout/', views.CartCashOutToOrder.as_view(), name='cart-check-out'),
    path('cart/checkout/delivery-fee/', views.calculate_delivery_fee, name='calculate-delivery-fee'),
    path('cart/checkout/get-coupon/', views.get_coupon_value, name='get-coupon'),
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
    path('orders/assign/to-caller/', views.assign_orders_to_caller, name='orders-assignment-caller'),
    path('orders/assign/to-agent/', views.assign_orders_to_delivery_guy, name='orders-assignment-delivery'),
    path('orders/lines/<int:pk>/update/', views.OrderLineUpdateView.as_view(), name='orderlines-line-details'),
    path('orders/lines/<int:pk>/delete/', views.OrderLineDeleteView.as_view(), name='orderlines-line-delete'),

    path('favorite/add/', views.FavoriteCreateView.as_view(), name='favorite-add'),
    path('favorite/list/', views.FavoriteListView.as_view(), name='favorite-list'),

    path('reviews/add/', views.AddReview.as_view(), name='review-add'),

    path('login-required/', views.LoginRequired.as_view(), name='login-required'),

    path('get-product-sizes/', views.get_product_sizes, name='get-product-sizes'),
    path("robots.txt", views.robots_txt),

]
