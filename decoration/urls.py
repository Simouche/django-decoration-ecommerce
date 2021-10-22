"""decoration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from decoration import settings
from ecommerce.models import Product

urlpatterns = [
                  path('i18n/', include('django.conf.urls.i18n')),
                  path('admin/', admin.site.urls),
                  path('', include('ecommerce.urls')),
                  path('account/', include('accounts.urls')),
                  path('sitemap.xml', sitemap,
                       {'sitemaps':
                           {
                               "product": GenericSitemap(
                                   {
                                       'queryset': Product.objects.filter(visible=True),
                                       'date_field': 'updated_at'
                                   }
                               )
                           },
                       }, name='django.contrib.sitemaps.views.sitemap')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "ecommerce.views.handle404"
handler403 = "ecommerce.views.handle403"
handler500 = "ecommerce.views.handle500"
