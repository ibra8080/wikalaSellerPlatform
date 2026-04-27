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
