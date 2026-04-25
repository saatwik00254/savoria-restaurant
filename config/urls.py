from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menu.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Serve media files in both dev and production
# On Render's free tier the filesystem is ephemeral but pre-committed
# media images (our food photos) will be present after each deploy
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
