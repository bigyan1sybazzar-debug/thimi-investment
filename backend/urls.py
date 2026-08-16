from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/deposits/', include('deposits.urls')),
    path('api/loans/', include('loans.urls')),
    path('api/investments/', include('investments.urls')),
    path('api/notifications/', include('notifications_app.urls')),


    # 🔥 ADD THIS (JWT AUTH)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('webui.urls')),
    path(
    "api/members/",include("members.urls"),),


    path(
        'admin-dashboard/',
        TemplateView.as_view(template_name='admin/dashboard.html'),
        name='admin-dashboard'
    ),

]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
