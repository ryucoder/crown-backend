"""crown_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from businesses.views import (
    BusinessViewset,
    BusinessAccountViewset,
    BusinessAddressViewset,
    BusinessContactViewset,
    OrderViewset,
)

from core.views import JobTypeViewset, StateViewset

from users.views import EmailUserViewset, RegisteredEmailUserViewset

default_router = DefaultRouter()
default_router.register(r"api/states", StateViewset, basename="states")
default_router.register(r"api/job-types", JobTypeViewset, basename="job-type")
default_router.register(r"api/businesses", BusinessViewset, basename="businesses")
default_router.register(
    r"api/business/accounts", BusinessAccountViewset, basename="business-accounts"
)
default_router.register(
    r"api/business/addresses", BusinessAddressViewset, basename="business-addresses"
)
default_router.register(
    r"api/business/contacts", BusinessContactViewset, basename="business-contacts"
)
default_router.register(r"api/orders", OrderViewset, basename="orders")
default_router.register(r"api/users", EmailUserViewset, basename="users")
default_router.register(
    r"api/users/registered", RegisteredEmailUserViewset, basename="regisitered_users"
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/obtain/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += default_router.urls


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
