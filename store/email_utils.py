from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_order_status_email(order, old_status=None):

    # =====================================================
    # STATUS DATA
    # =====================================================

    status_data = {

        "Pending": {
            "title": "Order Received",
            "message": (
                "Your order has been received successfully "
                "and is waiting for confirmation."
            ),
            "color": "#f59e0b",
            "bg": "#fffbeb",
            "icon": "📦",
        },

        "Confirmed": {
            "title": "Order Confirmed",
            "message": (
                "Your order has been confirmed "
                "and will be prepared shortly."
            ),
            "color": "#2563eb",
            "bg": "#eff6ff",
            "icon": "✓",
        },

        "Processing": {
            "title": "Your Order Is Being Processed",
            "message": (
                "Our team is currently preparing your order."
            ),
            "color": "#7c3aed",
            "bg": "#f5f3ff",
            "icon": "⚙️",
        },

        "Shipped": {
            "title": "Your Order Has Been Shipped",
            "message": (
                "Great news! Your package is now "
                "on its way to you."
            ),
            "color": "#0891b2",
            "bg": "#ecfeff",
            "icon": "🚚",
        },

        "Delivered": {
            "title": "Your Order Has Been Delivered",
            "message": (
                "Your order was delivered successfully. "
                "We hope you enjoy your purchase!"
            ),
            "color": "#16a34a",
            "bg": "#f0fdf4",
            "icon": "✓",
        },

        "Cancelled": {
            "title": "Your Order Has Been Cancelled",
            "message": (
                "Your ShopNex order has been cancelled."
            ),
            "color": "#dc2626",
            "bg": "#fef2f2",
            "icon": "✕",
        },
    }

    # =====================================================
    # CURRENT STATUS
    # =====================================================

    new_status = order.status

    data = status_data.get(new_status)

    if not data:
        print(f"Unknown order status: {new_status}")
        return False

    # =====================================================
    # CUSTOMER EMAIL
    # =====================================================

    if not order.email:
        print(f"Order #{order.id} has no customer email.")
        return False

    # =====================================================
    # CUSTOMER NAME
    # =====================================================

    customer_name = (
        order.full_name.strip().title()
        if order.full_name
        else "Customer"
    )

    # =====================================================
    # PROGRESS
    # =====================================================

    progress_map = {
        "Pending": 1,
        "Confirmed": 2,
        "Processing": 3,
        "Shipped": 4,
        "Delivered": 5,
        "Cancelled": 0,
    }

    progress = progress_map.get(new_status, 0)

    # =====================================================
    # CUSTOMER MESSAGE
    # =====================================================

    customer_message = data["message"]

    # =====================================================
    # ORDER URL
    # =====================================================

    order_url = ""

    if order.customer:

        order_url = (
            f"http://127.0.0.1:8000/orders/{order.id}/"
        )

    # =====================================================
    # EMAIL SUBJECT
    # =====================================================

    subject = (
        f"ShopNex Order #{order.id} - "
        f"{data['title']}"
    )

    # =====================================================
    # PLAIN TEXT
    # =====================================================

    message = f"""
Hello {customer_name},

Your ShopNex order has been updated.

ORDER DETAILS
================================

Order ID:
#{order.id}

Previous Status:
{old_status or "New Order"}

Current Status:
{new_status}

Order Total:
Rs. {order.total}

PAYMENT INFORMATION
================================

Payment Method:
{order.get_payment_method_display()}

Payment Status:
{order.get_payment_status_display()}

DELIVERY INFORMATION
================================

Name:
{order.full_name}

Phone:
{order.phone}

Address:
{order.address}

City:
{order.city}

Postal Code:
{order.postal_code}

================================

{customer_message}

Thank you for shopping with ShopNex.

ShopNex Team
"""

    # =====================================================
    # HTML EMAIL
    # =====================================================

    html_message = render_to_string(
        "emails/order_status.html",
        {
            "order": order,

            "old_status": (
                old_status
                if old_status
                else "New Order"
            ),

            "new_status": new_status,

            "status_title": data["title"],

            "status_message": data["message"],

            "status_color": data["color"],

            "status_bg": data["bg"],

            "status_icon": data["icon"],

            "customer_message": customer_message,

            "customer_name": customer_name,

            "progress": progress,

            "order_url": order_url,
        }
    )

    # =====================================================
    # EMAIL
    # =====================================================

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )

    email.attach_alternative(
        html_message,
        "text/html"
    )

    # =====================================================
    # SEND
    # =====================================================

    try:

        email.send(
            fail_silently=False
        )

    except Exception as e:

        print("")
        print("====================================")
        print("SHOPNEX STATUS EMAIL FAILED")
        print("====================================")
        print("Order:", order.id)
        print("To:", order.email)
        print("Old Status:", old_status)
        print("New Status:", new_status)
        print("Error:", str(e))
        print("====================================")

        raise

    print("")
    print("====================================")
    print("SHOPNEX STATUS EMAIL SENT")
    print("====================================")
    print("Order:", order.id)
    print("Customer:", customer_name)
    print("To:", order.email)
    print("Old Status:", old_status)
    print("New Status:", new_status)
    print("====================================")

    return True