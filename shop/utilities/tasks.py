import logging
from django.utils import timezone
from shop.models import Cart, Order, Ledger, Shipment
logger = logging.getLogger(__name__)


def get_amount(order):
    total_amount = 0
    for amount in order.product_id.values_list("product_price", flat=True):
        total_amount += amount
    return total_amount


def place_order(data):
    product = data["product"]
    required_product_count = data["product_count"]

    try:
        cart = Cart.objects.get(customer=data["customer"])
    except Cart.DoesNotExist:
        cart = Cart.objects.create(customer=data["customer"])

    try:
        order = Order.objects.get(cart=cart)
        if required_product_count > product.product_available_count:
            raise Exception("Not enough stock")
    except Order.DoesNotExist:
        order = Order.objects.create(cart=cart)
    except Exception as e:
        logger.error("Order not placed::error:{}".format(str(e)))
        return False
    order.product_id.add(product)

    # Update the stock after placing the order
    updated_available_count = product.product_available_count - required_product_count
    product.product_available_count = updated_available_count
    product.save()
    logger.info("Successfully placed order")

    # Update the ledger of customer
    total_amount = get_amount(order)
    order.amount = total_amount
    try:
        ledger = Ledger.objects.get(customer=data["customer"])
    except Ledger.DoesNotExist:
        ledger = Ledger.objects.create(customer=data["customer"],
                                       transaction_date=timezone.now())
    updated_amount = ledger.amount - total_amount
    ledger.amount = updated_amount
    ledger.save()

    # Update the shipment status
    try:
        shipment = Shipment.objects.get(order=order)
    except Shipment.DoesNotExist:
        shipment = Shipment.objects.create(order=order,
                                           status=Shipment.SHIPPED,
                                           shipment_date=timezone.now())
    shipment.status = Shipment.SHIPPED
    shipment.shipment_date = timezone.now()
    shipment.save()
    return True
