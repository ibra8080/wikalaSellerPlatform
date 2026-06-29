import resend
import os

resend.api_key = os.getenv('RESEND_API_KEY')

FROM_EMAIL = 'Wikala <noreply@wikala.net>'


def send_seller_approved(seller):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': seller.user.email,
            'subject': 'تم قبول طلب تسجيلك في وكالة 🎉',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {seller.full_name}،</h2>
                    <p>يسعدنا إخبارك بأنه تم قبول طلب تسجيلك كبائع في منصة وكالة.</p>
                    <p><strong>رقم البائع الخاص بك: {seller.seller_id}</strong></p>
                    <p>يمكنك الآن تسجيل الدخول وبدء إضافة منتجاتك.</p>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_seller_registration_received(seller):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': seller.user.email,
            'subject': 'We received your Wikala seller application ✓',
            'html': f'''
                <div>
                    <h2>Hello {seller.full_name},</h2>
                    <p>Thank you for applying to become a seller on Wikala. We have successfully received your application.</p>
                    <p>Our team will review it and get back to you by email within 2–3 business days.</p>
                    <p>No action is needed from you at this time.</p>
                    <br>
                    <p>The Wikala Team</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_seller_rejected(seller):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': seller.user.email,
            'subject': 'تحديث بخصوص طلب تسجيلك في وكالة',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {seller.full_name}،</h2>
                    <p>نأسف لإخبارك بأنه لم يتم قبول طلب تسجيلك في الوقت الحالي.</p>
                    <p><strong>السبب:</strong> {seller.rejection_reason}</p>
                    <p>يمكنك التواصل معنا لمزيد من التفاصيل.</p>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_product_approved(product):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': product.seller.user.email,
            'subject': f'تمت الموافقة على منتجك: {product.name_ar}',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {product.seller.full_name}،</h2>
                    <p>تمت الموافقة على منتجك بنجاح.</p>
                    <p><strong>اسم المنتج:</strong> {product.name_ar}</p>
                    <p><strong>كود المنتج:</strong> {product.product_code}</p>
                    <p>يرجى الآن إرسال البضاعة إلى مخزننا في مصر.</p>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_product_rejected(product):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': product.seller.user.email,
            'subject': f'تحديث بخصوص منتجك: {product.name_ar}',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {product.seller.full_name}،</h2>
                    <p>نأسف لإخبارك بأنه لم تتم الموافقة على منتجك.</p>
                    <p><strong>اسم المنتج:</strong> {product.name_ar}</p>
                    <p><strong>السبب:</strong> {product.rejection_reason}</p>
                    <p>يمكنك تعديل المنتج وإعادة تقديمه.</p>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_shipment_updated(product, to_status):
    try:
        status_labels = {
            'in_warehouse_egypt': 'وصل مخزن مصر',
            'in_transit': 'في الطريق إلى ألمانيا',
            'in_warehouse_germany': 'وصل مخزن ألمانيا — متاح للبيع',
            'listed': 'تم نشره على المنصة',
        }
        label = status_labels.get(to_status, to_status)
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': product.seller.user.email,
            'subject': f'تحديث شحن منتجك: {product.name_ar}',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {product.seller.full_name}،</h2>
                    <p>تم تحديث حالة شحن منتجك.</p>
                    <p><strong>المنتج:</strong> {product.name_ar}</p>
                    <p><strong>الحالة الجديدة:</strong> {label}</p>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_statement_ready(statement):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': statement.seller.user.email,
            'subject': f'كشف حسابك لشهر {statement.period_end} جاهز',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {statement.seller.full_name}،</h2>
                    <p>كشف حسابك الشهري جاهز.</p>
                    <p><strong>الفترة:</strong> {statement.period_start} — {statement.period_end}</p>
                    <p><strong>إجمالي المبيعات:</strong> {statement.total_sales} EUR</p>
                    <p><strong>صافي المستحق لك:</strong> {statement.net_amount} EUR</p>
                    <p>سيتم التحويل خلال 10 أيام عمل.</p>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")

def send_shipment_request_accepted(shipment_request):
    try:
        items_html = ''.join([
            f'<tr><td>{item.product.name_ar}</td><td>{item.product.product_code}</td><td>{item.cartons_count}</td><td>{item.total_units}</td></tr>'
            for item in shipment_request.items.all()
        ])

        delivery_methods = {
            'pickup': 'استلام بواسطة وكالة',
            'courier': 'شركة شحن',
            'drop_off': 'تسليم في مقر وكالة',
        }
        method_label = delivery_methods.get(shipment_request.delivery_method, shipment_request.delivery_method)

        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': shipment_request.seller.user.email,
            'subject': f'تم قبول طلب الشحن {shipment_request.request_number} ✅',
            'html': f'''
                <div dir="rtl">
                    <h2>مرحباً {shipment_request.seller.full_name}،</h2>
                    <p>تم قبول طلب الشحن الخاص بك.</p>
                    <p><strong>رقم الطلب:</strong> {shipment_request.request_number}</p>
                    <p><strong>موعد التسليم:</strong> {shipment_request.delivery_date}</p>
                    <p><strong>طريقة التسليم:</strong> {method_label}</p>
                    {f'<p><strong>ملاحظات:</strong> {shipment_request.delivery_notes}</p>' if shipment_request.delivery_notes else ''}
                    <br>
                    <h3>المنتجات:</h3>
                    <table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
                        <tr>
                            <th>المنتج</th>
                            <th>الكود</th>
                            <th>عدد الكراتين</th>
                            <th>إجمالي الوحدات</th>
                        </tr>
                        {items_html}
                    </table>
                    <br>
                    <p>فريق وكالة</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")

# ────────────────────────────────────────
# Widerruf (§ 356a BGB)
# ────────────────────────────────────────

WIDERRUF_ADMIN_EMAIL = 'wikala.market@gmail.com'


def send_widerruf_admin_notification(widerruf):
    """Notify admin that a new Widerruf request was received."""
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': WIDERRUF_ADMIN_EMAIL,
            'subject': f'Neuer Widerruf — Bestellung {widerruf.bestellnummer}',
            'html': f'''
                <div>
                    <h2>Neuer Widerruf eingegangen</h2>
                    <p><strong>Name:</strong> {widerruf.name}</p>
                    <p><strong>E-Mail:</strong> {widerruf.email}</p>
                    <p><strong>Bestellnummer:</strong> {widerruf.bestellnummer}</p>
                    <p><strong>Eingegangen am:</strong> {widerruf.created_at:%d.%m.%Y %H:%M:%S} UTC</p>
                    <p><strong>Erklärung des Kunden:</strong></p>
                    <p>{widerruf.widerrufserklaerung or '(keine)'}</p>
                    <hr>
                    <p style="color:#888;font-size:12px;">Datensatz-ID: {widerruf.id}</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Widerruf admin email error: {e}")


def send_widerruf_customer_confirmation(widerruf):
    """
    Send the customer an automatic Eingangsbestätigung (receipt confirmation).
    LEGAL: Confirms RECEIPT only, not acceptance/validity of the withdrawal.
    Must include the customer's declaration content and the exact timestamp.
    """
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': widerruf.email,
            'subject': f'Eingangsbestätigung Ihres Widerrufs — Bestellung {widerruf.bestellnummer}',
            'html': f'''
                <div>
                    <h2>Eingangsbestätigung</h2>
                    <p>Sehr geehrte/r {widerruf.name},</p>
                    <p>wir bestätigen den Eingang Ihrer Widerrufserklärung zu folgender Bestellung:</p>
                    <p><strong>Bestellnummer:</strong> {widerruf.bestellnummer}</p>
                    <p><strong>Eingegangen am:</strong> {widerruf.created_at:%d.%m.%Y um %H:%M:%S} Uhr (UTC)</p>
                    <p><strong>Inhalt Ihrer Erklärung:</strong></p>
                    <p>{widerruf.widerrufserklaerung or '(ohne zusätzliche Angaben)'}</p>
                    <hr>
                    <p style="color:#555;font-size:13px;">
                        Diese E-Mail bestätigt ausschließlich den Eingang Ihrer Erklärung.
                        Über die weitere Bearbeitung informieren wir Sie gesondert.
                    </p>
                    <p>Mit freundlichen Grüßen<br>Ihr Wikala-Team</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Widerruf customer email error: {e}")