from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from store.views import (
    about,
    contact,
    privacy_policy,
    terms,
    returns,
    shipping_info,
    faqs,
    order_tracking,
)

urlpatterns = [
    path('', views.home, name='home'),
     path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),
    # ==========================
    # WISHLIST
    # ==========================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),
path(
    "checkout/",
    views.checkout,
    name="checkout"
),

path(
    "order-success/<int:order_id>/",
    views.order_success,
    name="order_success"
),
path(
    "cart/",
    views.cart,
    name="cart"
),
path(
    "cart/remove/<int:item_id>/",
    views.remove_from_cart,
    name="remove_from_cart"
),
path(
    "cart/add/<int:product_id>/",
    views.add_to_cart,
    name="add_to_cart"
),

path(
    "cart/increase/<int:item_id>/",
    views.increase_cart,
    name="increase_cart"
),

path(
    "cart/decrease/<int:item_id>/",
    views.decrease_cart,
    name="decrease_cart"
),
path(
    "orders/",
    views.my_orders,
    name="my_orders"
),

path(
    "orders/<int:order_id>/",
    views.order_detail,
    name="order_detail"
),
path(
    "orders/<int:order_id>/tracking/",
    views.order_tracking,
    name="order_tracking"
),
path(
    "admin-dashboard/",
    views.admin_dashboard,
    name="admin_dashboard"
),
path(
    "dashboard/orders/<int:order_id>/status/",
    views.update_order_status,
    name="update_order_status"
),
path(
    "product/<int:product_id>/review/",
    views.add_review,
    name="add_review"
),
path("test-email/", views.test_email, name="test_email"),
path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),
 # LOGIN
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login"
    ),

    # LOGOUT
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),

    # -----------------------------
    # PASSWORD RESET
    # -----------------------------

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="/accounts/password-reset/done/"
        ),
        name="password_reset"
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/reset/done/"
        ),
        name="password_reset_confirm"
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),
path(
    "newsletter/subscribe/",
    views.newsletter_subscribe,
    name="newsletter_subscribe"
),
path(
    "about/",
    about,
    name="about"
),

path(
    "contact/",
    contact,
    name="contact"
),

path(
    "privacy-policy/",
    privacy_policy,
    name="privacy_policy"
),

path(
    "terms/",
    terms,
    name="terms"
),

path(
    "returns/",
    returns,
    name="returns"
),

path(
    "shipping-info/",
    shipping_info,
    name="shipping_info"
),

path(
    "faqs/",
    faqs,
    name="faqs"
),

path(
    "orders/<int:order_id>/tracking/",
    views.order_tracking,
    name="order_tracking_detail"
),
path(
    "track-order/",
    views.track_order,
    name="track_order"
),
path(
    "orders/<int:order_id>/tracking/",
    views.track_order_detail,
    name="track_order_detail"
),
path(
    "api/orders/<int:order_id>/",
    views.order_detail_api,
    name="order_detail_api"
),
path(
    "api/products/filter/",
    views.product_filter_api,
    name="product_filter_api"
),
]
if settings.DEBUG:
     urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
