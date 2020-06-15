from django.contrib import admin
from shop.models import (Category, Product, User, Address, Seller, Buyer, Cart, Order, Ledger, Shipment)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Address)
admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Ledger)
admin.site.register(Shipment)
