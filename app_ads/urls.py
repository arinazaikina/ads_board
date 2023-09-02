from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"ads", AdViewSet, basename="ad")
router.register(r"ads/(?P<ad_pk>\d+)/comments", ReviewViewSet, basename="ad-review")

urlpatterns = [path("", include(router.urls))]
