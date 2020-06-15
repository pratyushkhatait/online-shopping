from django.conf.urls import include, url
from rest_framework import routers
from shop.views import (Ping, Register, ProductViewSet, CategoryViewSet,
                        SellerViewSet, BuyerViewSet, OrderViewSet,
                        CancelShipmentView)

router = routers.DefaultRouter()
router.register(r'item', ProductViewSet, basename='item')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'seller', SellerViewSet, basename='seller')
router.register(r'buyer', BuyerViewSet, basename='buyer')
router.register(r'order', OrderViewSet, basename='order')

urlpatterns = [
    url(r'^', include((router.urls, 'shop'), namespace='shop')),
    # Ping Pong API
    url(r'^ping/$', Ping.as_view(), name='ping'),
    # Register user API
    url(r'^register-user/$', Register.as_view(), name='register-user'),
    # Cancel order
    url(r'^cancel-order/$', CancelShipmentView.as_view(), name='cancel-order')
]
