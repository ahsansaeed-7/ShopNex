from django.core.mail import send_mail
from django.conf import settings
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from reportlab.platypus import Image
from django.core.files.storage import default_storage
from reportlab.platypus import Image, Paragraph, Table

def send_order_confirmation(order):

    subject = f"ShopNex Order #{order.id} Confirmed"

    message = f"""
Hello {order.full_name},

Thank you for shopping with ShopNex!

Your order has been successfully placed.

Order ID: #{order.id}
Total: Rs. {order.total}
Payment Method: {order.payment_method}
Status: {order.status}

You can track your order from your ShopNex account.

Thank you for choosing ShopNex.

ShopNex Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )
def send_invoice_email(order):

    # ==========================================================
    # GET ORDER ITEMS
    # ==========================================================

    try:
        order_items = order.items.all()
    except AttributeError:
        order_items = order.orderitem_set.all()


    # ==========================================================
    # CREATE PDF IN MEMORY
    # ==========================================================

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )


    # ==========================================================
    # SHOPNEX COLORS
    # ==========================================================

    DARK = colors.HexColor("#05070D")
    BLUE = colors.HexColor("#3B82F6")
    LIGHT_BLUE = colors.HexColor("#EEF6FF")
    LIGHT_GRAY = colors.HexColor("#F7F9FC")
    BORDER = colors.HexColor("#E5EAF1")
    TEXT = colors.HexColor("#172033")
    MUTED = colors.HexColor("#718096")
    GREEN = colors.HexColor("#16A34A")
    WHITE = colors.white


    # ==========================================================
    # PDF STYLES
    # ==========================================================

    styles = getSampleStyleSheet()

    shopnex_style = ParagraphStyle(
        "ShopNex",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=WHITE,
        alignment=TA_LEFT,
    )

    invoice_style = ParagraphStyle(
        "Invoice",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=WHITE,
        alignment=TA_RIGHT,
    )

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=25,
        textColor=TEXT,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "ShopNexNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=MUTED,
    )

    small_style = ParagraphStyle(
        "ShopNexSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    )

    product_style = ParagraphStyle(
        "ProductName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=TEXT,
    )

    right_style = ParagraphStyle(
        "Right",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT,
        alignment=TA_RIGHT,
    )

    center_style = ParagraphStyle(
        "Center",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT,
        alignment=TA_CENTER,
    )

    total_style = ParagraphStyle(
        "Total",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=BLUE,
        alignment=TA_RIGHT,
    )


    # ==========================================================
    # PDF STORY
    # ==========================================================

    story = []


    # ==========================================================
    # HEADER
    # ==========================================================

    header_data = [[

        Paragraph(
            'Shop<span color="#3B82F6">Nex</span>',
            shopnex_style
        ),

        Paragraph(
            f"INVOICE<br/>"
            f"<font size='9'>#{order.id}</font>",
            invoice_style
        ),

    ]]

    header_table = Table(
        header_data,
        colWidths=[
            110 * mm,
            55 * mm,
        ],
        rowHeights=[
            30 * mm
        ],
    )

    header_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                DARK,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                15,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                15,
            ),
        ])
    )

    story.append(header_table)

    story.append(Spacer(1, 12))


    # ==========================================================
    # TITLE
    # ==========================================================

    story.append(
        Paragraph(
            "Your ShopNex Invoice",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"Thank you for shopping with ShopNex, "
            f"<b>{order.full_name}</b>.",
            normal_style
        )
    )

    story.append(Spacer(1, 18))


    # ==========================================================
    # CUSTOMER INFORMATION
    # ==========================================================

    customer_html = f"""
    <b>{order.full_name}</b><br/>
    {order.email}<br/>
    {order.phone}<br/>
    {order.address}<br/>
    {order.city}
    """

    order_info_html = f"""
    <b>Order ID:</b> #{order.id}<br/>
    <b>Payment:</b> {order.payment_method.title()}<br/>
    <b>Payment Status:</b> {order.payment_status.title()}<br/>
    <b>Order Status:</b> {order.status}
    """

    customer_table = Table(
        [[
            Paragraph(
                "<font color='#3B82F6'>"
                "<b>BILLED TO</b>"
                "</font>"
                "<br/><br/>"
                + customer_html,
                normal_style
            ),

            Paragraph(
                "<font color='#3B82F6'>"
                "<b>ORDER INFORMATION</b>"
                "</font>"
                "<br/><br/>"
                + order_info_html,
                normal_style
            ),
        ]],
        colWidths=[
            82 * mm,
            83 * mm,
        ],
    )

    customer_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                LIGHT_GRAY,
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),
        ])
    )

    story.append(customer_table)

    story.append(Spacer(1, 22))


    # ==========================================================
    # PRODUCT TABLE
    # ==========================================================

    product_data = [[

        Paragraph(
            "<b>PRODUCT</b>",
            small_style
        ),

        Paragraph(
            "<b>QTY</b>",
            ParagraphStyle(
                "HeaderCenter",
                parent=small_style,
                alignment=TA_CENTER,
            )
        ),

        Paragraph(
            "<b>PRICE</b>",
            ParagraphStyle(
                "HeaderRight1",
                parent=small_style,
                alignment=TA_RIGHT,
            )
        ),

        Paragraph(
            "<b>TOTAL</b>",
            ParagraphStyle(
                "HeaderRight2",
                parent=small_style,
                alignment=TA_RIGHT,
            )
        ),

    ]]


    for item in order_items:

        product = item.product

        product_name = getattr(
            product,
            "name",
            "Product"
        )

        quantity = item.quantity

        price = getattr(
            item,
            "price",
            None
        )

        if price is None:
            price = getattr(
                product,
                "price",
                0
            )

        item_total = price * quantity

        product_image = None

        if getattr(product, "image", None):

            try:

                product_image = Image(
                    product.image.path,
                    width=15 * mm,
                    height=15 * mm,
                )

            except Exception:

                product_image = None


        if product_image:

            product_cell = Table(
                [[
                    product_image,

                    Paragraph(
                        str(product_name),
                        product_style
                    ),
                ]],
                colWidths=[
                    18 * mm,
                    54 * mm,
                ],
            )

        else:

            product_cell = Paragraph(
                str(product_name),
                product_style
            )


        product_data.append([
            product_cell,

            Paragraph(
                str(quantity),
                center_style
            ),

            Paragraph(
                f"Rs. {price}",
                right_style
            ),

            Paragraph(
                f"Rs. {item_total}",
                ParagraphStyle(
                    "ItemTotal",
                    parent=right_style,
                    fontName="Helvetica-Bold",
                )
            ),
        ])


    product_table = Table(
        product_data,
        colWidths=[
            72 * mm,
            20 * mm,
            35 * mm,
            38 * mm,
        ],
        repeatRows=1,
    )

    product_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                LIGHT_GRAY,
            ),
            (
                "LINEBELOW",
                (0, 0),
                (-1, 0),
                0.8,
                BORDER,
            ),
            (
                "LINEBELOW",
                (0, 1),
                (-1, -1),
                0.4,
                BORDER,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
        ])
    )

    story.append(product_table)

    story.append(Spacer(1, 18))


    # ==========================================================
    # SHIPPING
    # ==========================================================

    if order.shipping == 0:
        shipping_text = "Free"
    else:
        shipping_text = f"Rs. {order.shipping}"


    # ==========================================================
    # TOTALS
    # ==========================================================

    totals_data = [

        [
            "",
            Paragraph(
                "Subtotal",
                normal_style
            ),
            Paragraph(
                f"Rs. {order.subtotal}",
                right_style
            ),
        ],

        [
            "",
            Paragraph(
                "Shipping",
                normal_style
            ),
            Paragraph(
                shipping_text,
                ParagraphStyle(
                    "Shipping",
                    parent=right_style,
                    textColor=GREEN,
                )
            ),
        ],

        [
            "",
            Paragraph(
                "<b>GRAND TOTAL</b>",
                ParagraphStyle(
                    "GrandLabel",
                    parent=normal_style,
                    fontName="Helvetica-Bold",
                    fontSize=11,
                    textColor=TEXT,
                    alignment=TA_RIGHT,
                )
            ),
            Paragraph(
                f"Rs. {order.total}",
                total_style
            ),
        ],
    ]


    totals_table = Table(
        totals_data,
        colWidths=[
            75 * mm,
            50 * mm,
            40 * mm,
        ],
    )

    totals_table.setStyle(
        TableStyle([
            (
                "LINEABOVE",
                (1, 2),
                (-1, 2),
                1.2,
                TEXT,
            ),
            (
                "TOPPADDING",
                (1, 2),
                (-1, 2),
                12,
            ),
            (
                "BOTTOMPADDING",
                (1, 2),
                (-1, 2),
                5,
            ),
        ])
    )

    story.append(totals_table)

    story.append(Spacer(1, 30))


    # ==========================================================
    # THANK YOU
    # ==========================================================

    thank_you = Table(
        [[
            Paragraph(
                "<b>Thank you for shopping with ShopNex.</b>"
                "<br/>"
                "We truly appreciate your order.",
                ParagraphStyle(
                    "ThankYou",
                    parent=normal_style,
                    alignment=TA_CENTER,
                    textColor=TEXT,
                )
            )
        ]],
        colWidths=[
            165 * mm
        ],
    )

    thank_you.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                LIGHT_BLUE,
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8E9FF"),
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                15,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                15,
            ),
        ])
    )

    story.append(thank_you)

    story.append(Spacer(1, 25))


    # ==========================================================
    # FOOTER
    # ==========================================================

    story.append(
        Paragraph(
            "ShopNex • Premium Shopping Experience",
            ParagraphStyle(
                "Footer",
                parent=small_style,
                alignment=TA_CENTER,
                textColor=MUTED,
            )
        )
    )


    # ==========================================================
    # BUILD PDF
    # ==========================================================

    document.build(story)

    pdf_buffer.seek(0)

    pdf_data = pdf_buffer.read()


    # ==========================================================
    # RENDER MODERN HTML EMAIL
    # ==========================================================

    html_content = render_to_string(
        "emails/invoice.html",
        {
            "order": order,
            "order_items": order_items,
        }
    )


    # ==========================================================
    # PLAIN TEXT FALLBACK
    # ==========================================================

    text_content = f"""
SHOPNEX
ORDER CONFIRMED

Hello {order.full_name},

Thank you for shopping with ShopNex.

Your order has been successfully placed.

Order ID: #{order.id}

Subtotal: Rs. {order.subtotal}
Shipping: Rs. {order.shipping}
Total: Rs. {order.total}

Payment Method: {order.payment_method}
Payment Status: {order.payment_status}
Order Status: {order.status}

Your PDF invoice is attached to this email.

Thank you for choosing ShopNex.

ShopNex Team
"""


    # ==========================================================
    # CREATE EMAIL
    # ==========================================================

    email = EmailMultiAlternatives(
        subject=f"ShopNex • Order #{order.id} Confirmed",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )


    # ==========================================================
    # ATTACH MODERN HTML EMAIL
    # ==========================================================

    email.attach_alternative(
        html_content,
        "text/html"
    )


    # ==========================================================
    # ATTACH PDF INVOICE
    # ==========================================================

    email.attach(
        f"ShopNex_Invoice_{order.id}.pdf",
        pdf_data,
        "application/pdf"
    )


    # ==========================================================
    # SEND
    # ==========================================================

    email.send(
        fail_silently=False
    )