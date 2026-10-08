from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .email_utils import send_order_status_email
from .models import (
    Product,
    Category,
    Wishlist,
    Order,
    OrderItem,
    Review,
)


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


# =========================================================
# PRODUCT
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "discount_price",
        "stock",
        "rating",
        "featured",
    )

    list_filter = (
        "category",
        "featured",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "price",
        "discount_price",
        "stock",
        "featured",
    )


# =========================================================
# WISHLIST
# =========================================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
    )

    search_fields = (
        "user__username",
        "product__name",
    )


# =========================================================
# ORDER
# =========================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "full_name",
        "total",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "payment_method",
        "payment_status",
        "status",
    )

    search_fields = (
        "full_name",
        "email",
        "phone",
        "customer__username",
        "customer__email",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        old_status = None

        # -----------------------------------------
        # GET OLD STATUS
        # -----------------------------------------

        if change:

            old_order = Order.objects.get(
                pk=obj.pk
            )

            old_status = old_order.status

        # -----------------------------------------
        # SAVE ORDER
        # -----------------------------------------

        super().save_model(
            request,
            obj,
            form,
            change
        )

        # -----------------------------------------
        # SEND EMAIL ONLY IF STATUS CHANGED
        # -----------------------------------------

        if (
            change
            and old_status != obj.status
        ):

            try:

                send_order_status_email(
                    obj,
                    old_status=old_status
                )

                self.message_user(
                    request,
                    (
                        f"Order #{obj.id} updated "
                        f"and status email sent."
                    )
                )

            except Exception as e:

                self.message_user(
                    request,
                    (
                        f"Order #{obj.id} updated, "
                        f"but email failed: {e}"
                    ),
                    level="error"
                )
                   # =====================================================
    # STATUS CHANGE EMAIL
    # =====================================================

    def save_model(self, request, obj, form, change):

        old_status = None

        if change:

            old_order = Order.objects.get(
                pk=obj.pk
            )

            old_status = old_order.status

        super().save_model(
            request,
            obj,
            form,
            change
        )

        # Send email only if status changed

        if change and old_status != obj.status:

            send_order_status_email(
    obj,
    old_status=old_status
)

    # =====================================================
    # SEND STATUS EMAIL
    # =====================================================

    
# =========================================================
# ORDER ITEM
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product_name",
        "price",
        "quantity",
        "total",
    )

    search_fields = (
        "product_name",
    )


# =========================================================
# REVIEW
# =========================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "user",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__username",
        "comment",
    )