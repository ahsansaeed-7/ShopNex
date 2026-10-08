from django.shortcuts import render
from django.db.models import Q
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncDate
from .email_utils import send_order_status_email
from datetime import timedelta
from django.utils import timezone
import json
from .models import Product, Category, Wishlist, Order, Cart ,OrderItem, Review
from .utils import send_order_confirmation
from django.core.mail import send_mail
from django.http import HttpResponse
from .utils import send_invoice_email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from .models import NewsletterSubscriber
from .models import Cart, Order
# Create your views here.
def home(request):

    products = Product.objects.all()

    categories = Category.objects.all()

    # -------------------------
    # SEARCH
    # -------------------------

    search = request.GET.get("search", "").strip()

    if search:
        products = products.filter(
            name__icontains=search
        )
    else:
        products = Product.objects.all()



    # -------------------------
    # CATEGORY
    # -------------------------

    category = request.GET.get("category", "")

    if category:
        products = products.filter(
            category__name__iexact=category
        )


    # -------------------------
    # MIN PRICE
    # -------------------------

    min_price = request.GET.get("min_price", "")

    if min_price:

        try:
            products = products.filter(
                price__gte=float(min_price)
            )

        except ValueError:
            pass


    # -------------------------
    # MAX PRICE
    # -------------------------

    max_price = request.GET.get("max_price", "")

    if max_price:

        try:
            products = products.filter(
                price__lte=float(max_price)
            )

        except ValueError:
            pass


    # -------------------------
    # RATING
    # -------------------------

    rating = request.GET.get("rating", "")

    if rating:

        try:
            products = products.filter(
                rating__gte=float(rating)
            )

        except ValueError:
            pass


    # -------------------------
    # SORTING
    # -------------------------

    sort = request.GET.get("sort", "")

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "newest":
        products = products.order_by("-id")

    elif sort == "rating":
        products = products.order_by("-rating")

    elif sort == "name":
        products = products.order_by("name")

# Latest products added by admin
    new_arrivals = Product.objects.filter(
        is_new_arrival=True
    ).order_by('-created_at')[:4]


    # Featured products
    featured_products = Product.objects.filter(
        featured=True
    )[:8]
    context = {

        "products": products,

        "categories": categories,

        "selected_category": category,

        "search": search,

        "min_price": min_price,

        "max_price": max_price,

        "selected_rating": rating,

        "selected_sort": sort,
        
        "new_arrivals": new_arrivals,
        
        "featured_products": featured_products,
    }
 

    return render(
        request,
        "home.html",
        context,
        
    )
# ==========================================
# WISHLIST
# ==========================================

@login_required(login_url="/accounts/login/")
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        "product",
        "product__category"
    )

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )

# ==========================================
# ADD TO WISHLIST
# ==========================================
@login_required(login_url="/accounts/login/")
def add_to_wishlist(request, product_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    if created:
        message = f"{product.name} added to wishlist."
    else:
        message = f"{product.name} is already in your wishlist."

    return JsonResponse({
        "success": True,
        "added": created,
        "message": message,
        "wishlist_count": wishlist_count
    })

# ==========================================
# REMOVE FROM WISHLIST
# ==========================================

@login_required(login_url="/accounts/login/")
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect("wishlist")
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    featured_products = Product.objects.filter(
        featured=True
    ).exclude(
        id=product.id
    )[:8]

    return render(request, 'product_detail.html', {
        'product': product,
        'featured_products': featured_products,
    })
# ==========================================
# CHECKOUT
# ==========================================


def checkout(request):

    # ==========================================
    # GET CART ITEMS
    # ==========================================

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product")

    else:

        cart_items = Cart.objects.filter(
            user=None,
            session_key=session_key
        ).select_related("product")

    # ==========================================
    # CHECK EMPTY CART
    # ==========================================

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # ==========================================
    # CALCULATE SUBTOTAL
    # ==========================================

    subtotal = Decimal("0.00")

    for item in cart_items:

        product = item.product

        if product.discount_price:
            price = product.discount_price
        else:
            price = product.price

        subtotal += price * item.quantity

    # ==========================================
    # SHIPPING
    # ==========================================

    shipping = Decimal("0.00")

    total = subtotal + shipping

    # ==========================================
    # PLACE ORDER
    # ==========================================

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        postal_code = request.POST.get(
            "postal_code",
            ""
        ).strip()

        # ==========================================
        # VALIDATE FORM
        # ==========================================

        if not all([
            full_name,
            email,
            phone,
            address,
            city
        ]):

            messages.error(
                request,
                "Please complete all required fields."
            )

            return render(
                request,
                "checkout.html",
                {
                    "cart_items": cart_items,
                    "subtotal": subtotal,
                    "shipping": shipping,
                    "total": total,
                }
            )

        # ==========================================
        # PAYMENT METHOD
        # ==========================================

        payment_method = request.POST.get(
            "payment_method",
            "cod"
        )

        if payment_method not in [
            "cod",
            "online"
        ]:

            payment_method = "cod"

        # ==========================================
        # CUSTOMER
        # ==========================================

        if request.user.is_authenticated:
            customer = request.user
        else:
            customer = None

        # ==========================================
        # CREATE ORDER
        # ==========================================

        with transaction.atomic():

            order = Order.objects.create(

                customer=customer,

                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                postal_code=postal_code,

                subtotal=subtotal,
                shipping=shipping,
                total=total,

                payment_method=payment_method,
                payment_status="pending",
                status="Pending",
            )

            # ==========================================
            # SAVE GUEST ORDER ID IN SESSION
            # ==========================================

            if not request.user.is_authenticated:

                guest_order_ids = request.session.get(
                    "guest_order_ids",
                    []
                )

                guest_order_ids.append(order.id)

                request.session["guest_order_ids"] = guest_order_ids
                request.session.modified = True

            # ==========================================
            # CREATE ORDER ITEMS
            # ==========================================

            for item in cart_items:

                product = item.product

                OrderItem.objects.create(

                    order=order,

                    product=product,

                    product_name=product.name,

                    price=product.final_price,

                    quantity=item.quantity,

                    total=item.item_total,
                )
             
            # ==========================================
            # SEND INVOICE EMAIL
            # ==========================================

            send_invoice_email(order)

            # ==========================================
            # PREPARE HTML EMAIL
            # ==========================================

            html_content = render_to_string(
                "emails/order_confirmation.html",
                {
                    "order": order,

                    "order_url": request.build_absolute_uri(
                        f"/orders/{order.id}/"
                    ),
                }
            )

            # ==========================================
            # PLAIN TEXT EMAIL
            # ==========================================

            text_content = f"""
Hello {order.full_name},

Thank you for shopping with ShopNex!

Your order has been successfully placed.

Order ID: #{order.id}

Subtotal: Rs. {order.subtotal}

Shipping: Rs. {order.shipping}

Total: Rs. {order.total}

Payment Method:
{order.payment_method}

Status:
{order.status}

We will notify you when your order is shipped.

Thank you for choosing ShopNex!

ShopNex Team
"""

            # ==========================================
            # CREATE EMAIL
            # ==========================================

            email_message = EmailMultiAlternatives(

                subject=f"ShopNex Order #{order.id} Confirmed",

                body=text_content,

                from_email=settings.DEFAULT_FROM_EMAIL,

                to=[order.email],
            )

            # ==========================================
            # ATTACH HTML EMAIL
            # ==========================================

            email_message.attach_alternative(
                html_content,
                "text/html"
            )

            # ==========================================
            # SEND EMAIL
            # ==========================================

            email_message.send(
                fail_silently=False
            )

            # ==========================================
            # CLEAR CART
            # ==========================================

            cart_items.delete()

        # ==========================================
        # SUCCESS MESSAGE
        # ==========================================

        messages.success(
            request,
            "Your order has been placed successfully!"
        )

        # ==========================================
        # REDIRECT TO ORDER SUCCESS
        # ==========================================

        return redirect(
            "order_success",
            order_id=order.id
        )

    # ==========================================
    # GET REQUEST - SHOW CHECKOUT
    # ==========================================

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
        }
    )
    
   
           

# ==========================================
# ORDER SUCCESS
# ==========================================


def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    # Logged-in user
    if request.user.is_authenticated:

        if order.customer_id != request.user.id:
            messages.error(
                request,
                "You are not allowed to view this order."
            )
            return redirect("home")

    # Guest user
    else:

        guest_order_ids = request.session.get(
            "guest_order_ids",
            []
        )

        if order.id not in guest_order_ids:
            messages.error(
                request,
                "You are not allowed to view this order."
            )
            return redirect("home")

    return render(
        request,
        "order_success.html",
        {
            "order": order
        }
    )
def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product")

    else:

        cart_items = Cart.objects.filter(
            user=None,
            session_key=session_key
        ).select_related("product")

    total = sum(
        item.item_total
        for item in cart_items
    )

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )

def remove_from_cart(request, item_id):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        item = get_object_or_404(
            Cart,
            id=item_id,
            user=request.user
        )

    else:

        item = get_object_or_404(
            Cart,
            id=item_id,
            user=None,
            session_key=session_key
        )

    if request.method == "POST":
        item.delete()

    return redirect("cart")
def add_to_cart(request, product_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Check stock
    if not product.in_stock:
        return JsonResponse({
            "success": False,
            "message": f"{product.name} is currently out of stock."
        })

    # Make sure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # ==========================================
    # LOGGED-IN USER
    # ==========================================

    if request.user.is_authenticated:

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={
                "session_key": None
            }
        )

        cart_items = Cart.objects.filter(
            user=request.user
        )

    # ==========================================
    # GUEST USER
    # ==========================================

    else:

        cart_item, created = Cart.objects.get_or_create(
            user=None,
            session_key=session_key,
            product=product
        )

        cart_items = Cart.objects.filter(
            user=None,
            session_key=session_key
        )

    # ==========================================
    # INCREASE QUANTITY
    # ==========================================

    if not created:
        cart_item.quantity += 1

    cart_item.save()

    # ==========================================
    # CART COUNT
    # ==========================================

    cart_count = sum(
        item.quantity
        for item in cart_items
    )

    return JsonResponse({
        "success": True,
        "message": f"{product.name} added to your cart.",
        "cart_count": cart_count
    })

def increase_cart(request, item_id):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        item = get_object_or_404(
            Cart,
            id=item_id,
            user=request.user
        )

    else:

        item = get_object_or_404(
            Cart,
            id=item_id,
            user=None,
            session_key=session_key
        )

    item.quantity += 1
    item.save()

    return redirect("cart")

def decrease_cart(request, item_id):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        item = get_object_or_404(
            Cart,
            id=item_id,
            user=request.user
        )

    else:

        item = get_object_or_404(
            Cart,
            id=item_id,
            user=None,
            session_key=session_key
        )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")
@login_required
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).order_by("-created_at")

    return render(
        request,
        "orders.html",
        {
            "orders": orders
        }
    )
    
 
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(
        request,
        "order_detail.html",
        {
            "order": order
        }
    )
# =========================================================
# ORDER DETAIL API - JSON
# =========================================================

@login_required(login_url="/accounts/login/")
def order_detail_api(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    )

    order_items = []

    for item in items:
        order_items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "price": str(item.price),
            "quantity": item.quantity,
            "total": str(item.total),
        })

    return JsonResponse({
        "success": True,

        "order": {
            "id": order.id,
            "full_name": order.full_name,
            "email": order.email,
            "phone": order.phone,
            "address": order.address,
            "city": order.city,
            "postal_code": order.postal_code,

            "subtotal": str(order.subtotal),
            "shipping": str(order.shipping),
            "total": str(order.total),

            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "status": order.status,

            "created_at": order.created_at.isoformat(),

            "items": order_items,
        }
    })
def order_tracking(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.user.is_authenticated:
        if order.customer_id != request.user.id:
            messages.error(
                request,
                "You are not allowed to view this order."
            )
            return redirect("home")

    else:
        guest_order_ids = request.session.get(
            "guest_order_ids",
            []
        )

        if order.id not in guest_order_ids:
            messages.error(
                request,
                "Please verify your Order ID and email first."
            )
            return redirect("track_order")

    return render(
        request,
        "order_tracking.html",
        {
            "order": order
        }
    )
@staff_member_required
def admin_dashboard(request):

    total_products = Product.objects.count()

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    total_orders = Order.objects.count()

    total_revenue = Order.objects.filter(
        status="Delivered"
    ).aggregate(
        total=Sum("total")
    )["total"] or 0

    pending_orders = Order.objects.filter(
        status="Pending"
    ).count()

    confirmed_orders = Order.objects.filter(
        status="Confirmed"
    ).count()

    processing_orders = Order.objects.filter(
        status="Processing"
    ).count()

    shipped_orders = Order.objects.filter(
        status="Shipped"
    ).count()

    delivered_orders = Order.objects.filter(
        status="Delivered"
    ).count()

    cancelled_orders = Order.objects.filter(
        status="Cancelled"
    ).count()


    # -----------------------------
    # LAST 7 DAYS SALES
    # -----------------------------

    today = timezone.localdate()

    seven_days_ago = today - timedelta(days=6)

    daily_sales = (
        Order.objects
        .filter(
            status="Delivered",
            created_at__date__gte=seven_days_ago,
            created_at__date__lte=today
        )
        .values("created_at__date")
        .annotate(
            revenue=Sum("total"),
            orders=Count("id")
        )
        .order_by("created_at__date")
    )


    sales_labels = []
    sales_data = []
    order_data = []

    for day in daily_sales:

        sales_labels.append(
            day["created_at__date"].strftime("%d %b")
        )

        sales_data.append(
            float(day["revenue"] or 0)
        )

        order_data.append(
            day["orders"]
        )


    # -----------------------------
    # ORDER STATUS DATA
    # -----------------------------

    status_labels = [
        "Pending",
        "Confirmed",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled",
    ]

    status_data = [
        pending_orders,
        confirmed_orders,
        processing_orders,
        shipped_orders,
        delivered_orders,
        cancelled_orders,
    ]


    # -----------------------------
    # RECENT ORDERS
    # -----------------------------

    recent_orders = Order.objects.select_related(
        "customer"
    ).order_by(
        "-created_at"
    )[:8]


    # -----------------------------
    # LOW STOCK
    # -----------------------------

    low_stock_products = Product.objects.filter(
        stock__lte=5
    ).order_by(
        "stock"
    )[:8]


    context = {

        "total_products": total_products,

        "total_customers": total_customers,

        "total_orders": total_orders,

        "total_revenue": total_revenue,

        "pending_orders": pending_orders,

        "confirmed_orders": confirmed_orders,

        "processing_orders": processing_orders,

        "shipped_orders": shipped_orders,

        "delivered_orders": delivered_orders,

        "cancelled_orders": cancelled_orders,

        "recent_orders": recent_orders,

        "low_stock_products": low_stock_products,

        # Charts

        "sales_labels": json.dumps(sales_labels),

        "sales_data": json.dumps(sales_data),

        "order_data": json.dumps(order_data),

        "status_labels": json.dumps(status_labels),

        "status_data": json.dumps(status_data),
    }


    return render(
        request,
        "admin_dashboard.html",
        context
    )
@login_required
def add_review(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if not rating or not comment:
            messages.error(
                request,
                "Please provide a rating and review."
            )
            return redirect("product_detail", product_id=product.id)

        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                "rating": rating,
                "comment": comment,
            }
        )

        if created:
            messages.success(
                request,
                "Your review has been added."
            )
        else:
            messages.success(
                request,
                "Your review has been updated."
            )

    return redirect("product_detail", product_id=product.id)
def test_email(request):

    send_mail(
        subject="ShopNex Test Email",
        message="""
Hello!

This is a test email from ShopNex.

Your real email system is working successfully.

ShopNex
        """,
        from_email=None,
        recipient_list=["YOUR_PERSONAL_EMAIL@gmail.com"],
        fail_silently=False,
    )

    return HttpResponse("Email sent successfully!")
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

# Make sure Order is already imported in your views.py
# from .models import Order

@staff_member_required
def update_order_status(request, order_id):

    if request.method != "POST":
        return redirect("admin_dashboard")

    order = get_object_or_404(
        Order,
        id=order_id
    )

    new_status = request.POST.get("status")

    if not new_status:
        messages.error(
            request,
            "Please select an order status."
        )

        return redirect("admin_dashboard")

    # -----------------------------------------
    # CHECK VALID STATUS
    # -----------------------------------------

    valid_statuses = dict(
        Order.STATUS_CHOICES
    )

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid order status."
        )

        return redirect("admin_dashboard")

    # -----------------------------------------
    # OLD STATUS
    # -----------------------------------------

    old_status = order.status

    # -----------------------------------------
    # NOTHING CHANGED
    # -----------------------------------------

    if old_status == new_status:

        messages.info(
            request,
            f"Order #{order.id} is already {new_status}."
        )

        return redirect("admin_dashboard")

    # -----------------------------------------
    # UPDATE ORDER
    # -----------------------------------------

    order.status = new_status

    order.save(
        update_fields=["status"]
    )

    # -----------------------------------------
    # SEND EMAIL
    # -----------------------------------------

    try:

        send_order_status_email(
            order,
            old_status
        )

        messages.success(
            request,
            f"Order #{order.id} updated to "
            f"{new_status}. Customer email sent."
        )

    except Exception as e:

        print("====================================")
        print("SHOPNEX EMAIL ERROR")
        print("Order:", order.id)
        print("Error:", str(e))
        print("====================================")

        messages.warning(
            request,
            f"Order updated to {new_status}, "
            f"but email could not be sent."
        )

    return redirect("admin_dashboard")
def newsletter_subscribe(request):

    if request.method != "POST":
        return redirect("home")

    # ==========================================
    # GET EMAIL
    # ==========================================

    subscriber_email = request.POST.get("email", "").strip().lower()

    print("================================")
    print("NEWSLETTER SUBSCRIPTION")
    print("Email entered:", subscriber_email)
    print("================================")

    if not subscriber_email:

        messages.error(
            request,
            "Please enter your email address."
        )

        return redirect("home")


    # ==========================================
    # SAVE SUBSCRIBER
    # ==========================================

    try:

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=subscriber_email
        )

        print("Subscriber created:", created)
        print("Subscriber ID:", subscriber.id)

    except Exception as e:

        print("DATABASE ERROR:", e)

        messages.error(
            request,
            "Something went wrong. Please try again."
        )

        return redirect("home")


    # ==========================================
    # CUSTOMER EMAIL
    # ==========================================

    customer_html = render_to_string(
        "emails/newsletter_welcome.html",
        {
            "subscriber_email": subscriber_email,
            "subscriber": subscriber,
        }
    )


    customer_text = f"""
Hello!

Welcome to ShopNex.

You have successfully subscribed to our newsletter.

You will now receive updates about:

• New products
• Special offers
• Latest collections
• Exclusive ShopNex updates

Subscribed email:
{subscriber_email}

Thank you for joining ShopNex!

ShopNex Team
"""


    # ==========================================
    # SEND CUSTOMER EMAIL
    # ==========================================

    try:

        customer_email = EmailMultiAlternatives(

            subject="Welcome to ShopNex Newsletter ✨",

            body=customer_text,

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[
                subscriber_email
            ],
        )

        customer_email.attach_alternative(
            customer_html,
            "text/html"
        )

        customer_result = customer_email.send(
            fail_silently=False
        )

        print("================================")
        print("CUSTOMER NEWSLETTER EMAIL")
        print("To:", subscriber_email)
        print("Send Result:", customer_result)
        print("================================")


    except Exception as e:

        print("================================")
        print("CUSTOMER EMAIL ERROR")
        print("ERROR:", e)
        print("================================")

        customer_result = 0


    # ==========================================
    # ADMIN EMAIL
    # ==========================================

    admin_html = render_to_string(
        "emails/newsletter_subscription.html",
        {
            "subscriber_email": subscriber_email,
            "subscriber": subscriber,
        }
    )


    admin_text = f"""
SHOPNEX NEWSLETTER

New Newsletter Subscriber

Email:
{subscriber_email}

Subscriber ID:
#{subscriber.id}

A new customer has subscribed to the ShopNex newsletter.
"""


    try:

        admin_email = EmailMultiAlternatives(

            subject="ShopNex — New Newsletter Subscriber",

            body=admin_text,

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[
                settings.NEWSLETTER_ADMIN_EMAIL
            ],
        )

        admin_email.attach_alternative(
            admin_html,
            "text/html"
        )

        admin_result = admin_email.send(
            fail_silently=False
        )

        print("================================")
        print("ADMIN NEWSLETTER EMAIL")
        print("To:", settings.NEWSLETTER_ADMIN_EMAIL)
        print("Send Result:", admin_result)
        print("================================")


    except Exception as e:

        print("================================")
        print("ADMIN EMAIL ERROR")
        print("ERROR:", e)
        print("================================")

        admin_result = 0


    # ==========================================
    # MESSAGE
    # ==========================================

    if customer_result == 1:

        messages.success(
            request,
            "You're subscribed! Check your email for confirmation."
        )

    else:

        messages.warning(
            request,
            "You are subscribed, but the confirmation email could not be sent."
        )


    return redirect("home")
# =========================================================
# FOOTER PAGES
# =========================================================

def about(request):
    return render(request, "footer/about.html")


# =========================================================
# CONTACT PAGE
# =========================================================

def contact(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        subject = request.POST.get(
            "subject",
            ""
        ).strip()

        message = request.POST.get(
            "message",
            ""
        ).strip()


        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not all([
            name,
            email,
            message
        ]):

            messages.error(
                request,
                "Please complete all required fields."
            )

            return render(
                request,
                "footer/contact.html"
            )


        # -----------------------------
        # EMAIL TO SHOPNEX
        # -----------------------------

        email_subject = (
            f"ShopNex Contact: "
            f"{subject or 'New Message'}"
        )


        email_message = f"""
SHOPNEX CONTACT FORM
====================

Name:
{name}

Email:
{email}

Subject:
{subject or 'No subject'}

Message:
{message}

====================
ShopNex Website
"""


        try:

            send_mail(

                subject=email_subject,

                message=email_message,

                from_email=None,

                recipient_list=[
                    settings.DEFAULT_FROM_EMAIL
                ],

                fail_silently=False,
            )


            messages.success(
                request,
                "Your message has been sent successfully. "
                "We will get back to you soon."
            )


        except Exception as e:

            print(
                "CONTACT EMAIL ERROR:",
                e
            )

            messages.error(
                request,
                "We couldn't send your message right now. "
                "Please try again later."
            )


        return redirect("contact")


    return render(
        request,
        "footer/contact.html"
    )

def privacy_policy(request):
    return render(request, "footer/privacy_policy.html")


def terms(request):
    return render(request, "footer/terms.html")


def returns(request):
    return render(request, "footer/returns.html")


def shipping_info(request):
    return render(request, "footer/shipping_info.html")


def faqs(request):
    return render(request, "footer/faqs.html")


def track_order(request):

    if request.method == "POST":

        order_id = request.POST.get("order_id", "").strip()
        email = request.POST.get("email", "").strip()

        if not order_id or not email:
            messages.error(
                request,
                "Please enter your Order ID and email."
            )
            return render(
                request,
                "footer/order_tracking.html"
            )

        order = Order.objects.filter(
            id=order_id,
            email__iexact=email
        ).first()

        if order:
            guest_order_ids = request.session.get(
                "guest_order_ids",
                []
            )

            if order.id not in guest_order_ids:
                guest_order_ids.append(order.id)
                request.session["guest_order_ids"] = guest_order_ids
                request.session.modified = True

            return redirect(
                "track_order_detail",
                order_id=order.id
            )

        messages.error(
            request,
            "Order not found. Please check your Order ID and email."
        )

    return render(
        request,
        "footer/order_tracking.html"
    )
    
def track_order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.user.is_authenticated:

        if order.customer_id != request.user.id:
            messages.error(
                request,
                "You are not allowed to view this order."
            )
            return redirect("home")

    else:

        guest_order_ids = request.session.get(
            "guest_order_ids",
            []
        )

        if order.id not in guest_order_ids:
            messages.error(
                request,
                "Please verify your Order ID and email first."
            )
            return redirect( "track_order_detail",
    order_id=order.id)

    return render(
        request,
        "order_tracking.html",
        {
            "order": order
        }
    )
    
    # =========================================================
# PRODUCT FILTER API - JSON
# =========================================================

def product_filter_api(request):

    products = Product.objects.all()

    # SEARCH
    search = request.GET.get("search", "").strip()

    if search:
        products = products.filter(
            name__icontains=search
        )

    # CATEGORY
    category = request.GET.get("category", "").strip()

    if category:
        products = products.filter(
            category__name__iexact=category
        )

    # MIN PRICE
    min_price = request.GET.get("min_price", "").strip()

    if min_price:
        try:
            products = products.filter(
                price__gte=Decimal(min_price)
            )
        except:
            pass

    # MAX PRICE
    max_price = request.GET.get("max_price", "").strip()

    if max_price:
        try:
            products = products.filter(
                price__lte=Decimal(max_price)
            )
        except:
            pass

    # RATING
    rating = request.GET.get("rating", "").strip()

    if rating:
        try:
            products = products.filter(
                rating__gte=Decimal(rating)
            )
        except:
            pass

    # SORT
    sort = request.GET.get("sort", "")

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "newest":
        products = products.order_by("-id")

    elif sort == "rating":
        products = products.order_by("-rating")

    elif sort == "name":
        products = products.order_by("name")

    # JSON DATA
    product_data = []

    for product in products:

        product_data.append({
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "discount_price": (
                str(product.discount_price)
                if product.discount_price
                else None
            ),
            "rating": float(product.rating or 0),
            "image": product.image.url if product.image else "",
            "in_stock": product.in_stock,
        })

    return JsonResponse({
        "success": True,
        "count": len(product_data),
        "products": product_data
    })