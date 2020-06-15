import logging
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import HttpResponse
from shop.serializers import (RegisterSerializer, ProductCreateSerializer,
                              CategoryCreateSerializer, SellerCreateSerializer,
                              BuyerCreateSerializer, OrderCreateSerializer,
                              ShipmentSerializer)
from shop.models import (User, Address, Product, Category, Seller, Buyer, Ledger, Cart, Order, Shipment)
from shop.utilities.tasks import place_order
logger = logging.getLogger(__name__)


class Ping(APIView):
    http_method_names = ['get']

    def get(self):
        return HttpResponse("Pong")


class Register(APIView):
    http_method_names = ['post']
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer_obj = self.serializer_class(data=request.GET)
        try:
            serializer_obj.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(resp, status=status_code)
        validated_data = serializer_obj.validated_data
        try:
            user = User.objects.get(name=validated_data['name'],
                                    email=validated_data['email'],
                                    phone=validated_data['phone'])
            logger.info("Register: User:{} already exists".format(user.name))
            resp = {
                'detail': "User already exits"
            }
            status_code = status.HTTP_200_OK
        except User.DoesNotExist:
            try:
                address = Address.objects.get(street=validated_data['street'],
                                              zip_code=validated_data['zip_code'])
            except Address.DoesNotExist:
                address = Address.objects.create(street=validated_data['street'],
                                                 zip_code=validated_data['zip_code'],
                                                 city=validated_data['city'],
                                                 state=validated_data['state'],
                                                 country=validated_data['country'])
            user = User.objects.create(name=validated_data['name'],
                                       email=validated_data['email'],
                                       phone=validated_data['phone'],
                                       shipping_address=address)

            resp = {
                'detail': "User successfully created"
            }
            status_code = status.HTTP_200_OK
            logger.info("Register: Successfully added user:{}".format(user.name))

        return Response(data=resp, status=status_code)


class CategoryViewSet(viewsets.ViewSet):
    serializer_create_class = CategoryCreateSerializer
    http_method_names = ['get', 'post', 'delete']

    def create(self, request):
        category_serializer = self.serializer_create_class(data=request.GET)
        try:
            category_serializer.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(resp, status=status_code)
        validated_data = category_serializer.validated_data
        try:
            cat = Category.objects.get(name=validated_data['name'])
            resp = {
                'detail': "Category already exits"
            }
            status_code = status.HTTP_200_OK
            logger.info("Category: Category:{} already exits".format(cat.name))
        except Category.DoesNotExist:
            cat = Category.objects.create(name=validated_data['name'])
            resp = {
                "detail": "Category created successfully"
            }
            status_code = status.HTTP_200_OK
            logger.info("Category: Successfully added user:{}".format(cat.name))

        return Response(data=resp, status=status_code)

    def destroy(self, request, pk):
        logger.info("CategoryViewSet: deleted category_id:{}".format(pk))
        try:
            Category.objects.filter(id=pk).delete()
            resp = {
                'detail': 'Category successfully deleted'
            }
            status_code = status.HTTP_200_OK
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as excep:
            resp = {
                'detail': str(excep)
            }
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(data=resp, status=status_code)


class SellerViewSet(viewsets.ViewSet):
    serializer_create_class = SellerCreateSerializer
    http_method_names = ['post', 'delete']

    def create(self, request):
        payload = request.data
        product_serializer = self.serializer_create_class(data=payload)
        try:
            product_serializer.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(data=resp, status=status_code)

        validated_data = product_serializer.validated_data
        try:
            seller = Seller.objects.get(seller_id=validated_data["account"])
            seller.user_name = validated_data["user_name"]
            seller.password = validated_data["password"]
            logger.info("SellerViewSet: Successfully updated the seller account:{}".format(seller.user_name))
            resp = {
                "detail": "Successfully update the seller account"
            }
            status_code = status.HTTP_200_OK
        except Seller.DoesNotExist:
            seller = Seller.objects.create(seller_id=validated_data["account"],
                                           user_name=validated_data["user_name"],
                                           password=validated_data["password"])
            logger.info("SellerViewSet: Successfully created seller account: {}".format(seller.user_name))
            resp = {
                "detail": "successfully created seller account"
            }
            status_code = status.HTTP_200_OK
        return Response(data=resp, status=status_code)

    def destroy(self, request, pk):
        try:
            Seller.objects.filter(id=pk).delete()
            resp = {
                'detail': 'Seller successfully deleted'
            }
            status_code = status.HTTP_200_OK
            logger.info("SellerViewSet: deleted seller_id:{}".format(pk))
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as excep:
            resp = {
                'detail': str(excep)
            }
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(data=resp, status=status_code)


class BuyerViewSet(viewsets.ViewSet):
    serializer_create_class = BuyerCreateSerializer
    http_method_names = ['post', 'delete']

    def create(self, request):
        payload = request.data
        product_serializer = self.serializer_create_class(data=payload)
        try:
            product_serializer.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(data=resp, status=status_code)

        validated_data = product_serializer.validated_data
        try:
            buyer = Buyer.objects.get(buyer_id=validated_data["account"])
            logger.info("SellerViewSet: buyer already existst:{}".format(buyer.buyer_id))
            resp = {
                "detail": "Buyer already exists"
            }
            status_code = status.HTTP_200_OK
        except Buyer.DoesNotExist:
            buyer = Buyer.objects.create(buyer_id=validated_data["account"])
            logger.info("SellerViewSet: Successfully created buyer account: {}".format(buyer.buyer_id))
            resp = {
                "detail": "successfully created buyer account"
            }
            status_code = status.HTTP_200_OK
        return Response(data=resp, status=status_code)

    def destroy(self, request, pk):
        try:
            Buyer.objects.filter(id=pk).delete()
            resp = {
                'detail': 'Buyer successfully deleted'
            }
            status_code = status.HTTP_200_OK
            logger.info("SellerViewSet: deleted buyer_id:{}".format(pk))
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as excep:
            resp = {
                'detail': str(excep)
            }
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(data=resp, status=status_code)


class ProductViewSet(viewsets.ViewSet):
    serializer_create_class = ProductCreateSerializer
    http_method_names = ['post', 'delete']

    def create(self, request):
        payload = request.data
        product_serializer = self.serializer_create_class(data=payload)
        try:
            product_serializer.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(data=resp, status=status_code)

        validated_data = product_serializer.validated_data
        try:
            product = Product.objects.get(product_name=validated_data['product_name'],
                                          product_seller=validated_data['seller'])
            product.product_price = validated_data['product_price']
            product.product_available_count += validated_data['product_available_count']
            product.save()
            logger.info("ProductViewSet: updated product:{}".format(product.product_name))
            resp = {
                "detail": "Successfully updated the product"
            }
            status_code = status.HTTP_200_OK
        except Product.DoesNotExist:
            product = Product.objects.create(product_name=validated_data['product_name'],
                                             product_description=validated_data['product_description'],
                                             product_price=validated_data['product_price'],
                                             product_available_count=validated_data['product_available_count'],
                                             product_seller=validated_data['seller'],
                                             category=validated_data['category'])
            logger.info("ProductViewSet: Successfully added Product:{}".format(product.product_name))
            resp = {
                "detail": "Successfully Added the product"
            }
            status_code = status.HTTP_200_OK
        return Response(data=resp, status=status_code)

    def destroy(self, request, pk):
        try:
            Product.objects.filter(id=pk).delete()
            resp = {
                'detail': 'Product successfully deleted'
            }
            status_code = status.HTTP_200_OK
            logger.info("SellerViewSet: deleted product_id:{}".format(pk))
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as excep:
            resp = {
                'detail': str(excep)
            }
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(data=resp, status=status_code)


class OrderViewSet(viewsets.ViewSet):
    serializer_create_class = OrderCreateSerializer
    http_method_names = ['post', 'delete']

    def create(self, request):
        payload = request.data
        order_serializer = self.serializer_create_class(data=payload)
        try:
            order_serializer.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(data=resp, status=status_code)

        validated_data = order_serializer.validated_data
        order_status = place_order(validated_data)
        if order_status is True:
            resp = {
                "detail": "Successfully added item to cart"
            }
            status_code = status.HTTP_200_OK
            logger.info("CartViewSet: Successfully addded product:{} into cart of customer:{}"
                        .format(validated_data["product"], validated_data["customer"]))
        else:
            resp = {
                "detail": "Not able to add item to cart"
            }
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(data=resp, status=status_code)


class CancelShipmentView(APIView):
    http_method_names = ['post']
    serializer_class = ShipmentSerializer

    def post(self, request):
        serializer_obj = self.serializer_class(data=request.data)
        try:
            serializer_obj.is_valid(raise_exception=True)
        except ValidationError as excep:
            resp = {
                'detail': excep.detail
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(resp, status=status_code)
        validated_data = serializer_obj.validated_data
        order = validated_data["order"]
        try:
            shipment = Shipment.objects.get(order=order)
        except Shipment.DoesNotExist:
            resp = {
                "detail": "Not able to cancel the shipment"
            }
            logger.error("CancelShipmentView: Not able to cancel the shipment for order:{}".format(order))
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(data=resp, status=status_code)
        today = timezone.now()
        # Assuming shipment gets delivered in 7 days of it's departure
        # So you have to cancel withing 7 days if required
        if (today - shipment.shipment_date) < 7:
            shipment.status = Shipment.CANCELED
            shipment.shipment_date = timezone.now()

            # Adjust the ledger accordingly
            try:
                ledger = Ledger.objects.get(customer=validated_data["customer"])
            except Ledger.DoesNotExist:
                logger.error("CancelShipmentView: Ledger not found, shipment cannot be cancelled")
                resp = {
                    "detail": "Not able to cancel the shipment"
                }
                logger.error("CancelShipmentView: Not able to cancel the shipment for order:{}".format(order))
                status_code = status.HTTP_400_BAD_REQUEST
                return Response(data=resp, status=status_code)
            updated_amount = ledger.amount + order.amount
            ledger.amount = updated_amount
            ledger.save()
            shipment.save()
            resp = {
                "detail": "Shipment cancelled successfully"
            }
            status_code = status.HTTP_200_OK
        else:
            shipment.status = Shipment.COMPLETED
            shipment.shipment_date = today
            shipment.save()
            resp = {
                "detail": "Shipment already delivered"
            }
            status_code = status.HTTP_200_OK
        return Response(data=resp, status=status_code)
