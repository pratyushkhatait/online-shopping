from rest_framework import serializers
from shop.models import Category, Seller, User, Product, Buyer, Order, Cart


class CustomBaseSerializer(serializers.Serializer):

    def validate(self, data):
        return super().validate(data)


class RegisterSerializer(CustomBaseSerializer):
    name = serializers.CharField(max_length=50, required=True)
    email = serializers.CharField(max_length=50, required=True)
    phone = serializers.CharField(max_length=50, required=True)

    street = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=50, required=False)
    state = serializers.CharField(max_length=50, required=False)
    zip_code = serializers.IntegerField(required=False)
    country = serializers.CharField(max_length=50, required=False)


class CategoryCreateSerializer(CustomBaseSerializer):
    name = serializers.CharField(max_length=50, required=True)


class SellerCreateSerializer(CustomBaseSerializer):
    user_name = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(max_length=10, required=True)
    name = serializers.CharField(max_length=50, required=True)
    phone = serializers.CharField(max_length=10, required=True)

    def validate(self, data):
        try:
            account = User.objects.get(name=data["name"],
                                       phone=data["phone"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not registered. Register First!")
        data["account"] = account
        return super().validate(data)


class BuyerCreateSerializer(CustomBaseSerializer):
    name = serializers.CharField(max_length=50, required=True)
    phone = serializers.CharField(max_length=50, required=True)

    def validate(self, data):
        try:
            account = User.objects.get(name=data["name"],
                                       phone=data["phone"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not registered. Register First!")
        data["account"] = account
        return super().validate(data)


class ProductCreateSerializer(CustomBaseSerializer):
    product_name = serializers.CharField(max_length=50, required=True)
    product_description = serializers.CharField(allow_null=True, required=False)
    product_price = serializers.FloatField(required=True)
    product_available_count = serializers.IntegerField(required=True)
    category_name = serializers.CharField(max_length=50, required=True)
    seller_user_name = serializers.CharField(max_length=60, required=True)

    def validate(self, data):
        try:
            cat = Category.objects.get(name=data['category_name'])
        except Category.DoesNotExist:
            raise serializers.ValidationError('Invalid Category')

        try:
            seller = Seller.objects.get(user_name=data["seller_user_name"])
        except Seller.DoesNotExist:
            raise serializers.ValidationError('Invalid Seller')
        data['category'] = cat
        data['seller'] = seller
        return super().validate(data)


class OrderCreateSerializer(CustomBaseSerializer):
    name = serializers.CharField(max_length=50, required=True)
    phone = serializers.CharField(max_length=50, required=True)
    product_name = serializers.CharField(max_length=50, required=True)
    product_description = serializers.CharField(max_length=100, required=True)
    category_name = serializers.CharField(max_length=50, required=True)
    product_count = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            account = User.objects.get(name=data["name"],
                                       phone=data["phone"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not registered. Register First!")

        try:
            buyer = Buyer.objects.get(buyer_id=account)
        except Buyer.DoesNotExist:
            raise serializers.ValidationError("Buyer is not registered")

        try:
            cat = Category.objects.get(name=data['category_name'])
        except Category.DoesNotExist:
            raise serializers.ValidationError('Invalid Category')

        try:
            product = Product.objects.get(product_name=data["product_name"],
                                          product_description=data["product_description"],
                                          category=cat)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product Not found")
        data["customer"] = buyer
        data["product"] = product
        return super().validate(data)


class ShipmentSerializer(CustomBaseSerializer):
    name = serializers.CharField(max_length=50, required=True)
    phone = serializers.CharField(max_length=50, required=True)

    def validate(self, data):
        try:
            account = User.objects.get(name=data["name"],
                                       phone=data["phone"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not registered. Register First!")

        try:
            buyer = Buyer.objects.get(buyer_id=account)
        except Buyer.DoesNotExist:
            raise serializers.ValidationError("Buyer is not registered")

        try:
            cart = Cart.objects.get(cart=buyer)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart doesnot exist")

        try:
            order = Order.objects.get(order=cart)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order doesnot exist")
        data["customer"] = buyer
        data["order"] = order
        return super().validate(data)
