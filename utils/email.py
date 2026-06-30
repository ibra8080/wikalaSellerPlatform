import resend
import os

resend.api_key = os.getenv('RESEND_API_KEY')

FROM_EMAIL = 'Wikala <noreply@wikala.net>'


def send_seller_approved(seller):
    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': seller.user.email,
            'subject': 'Your Wikala seller application has been approved 🎉',
            'html': f'''
                <div>
                    <h2>Hello {seller.full_name},</h2>
                    <p>We're pleased to let you know that your application to become a seller on Wikala has been approved.</p>
                    <p><strong>Your seller ID: {seller.seller_id}</strong></p>
                    <p>You can now log in and start adding your products.</p>
                    <br>
                    <p>The Wikala Team</p>
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
            'subject': 'Update on your Wikala seller application',
            'html': f'''
                <div>
                    <h2>Hello {seller.full_name},</h2>
                    <p>We're sorry to inform you that your seller application was not approved at this time.</p>
                    <p><strong>Reason:</strong> {seller.rejection_reason}</p>
                    <p>You're welcome to contact us for more details.</p>
                    <br>
                    <p>The Wikala Team</p>
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
            'subject': f'Your product has been approved: {product.name_en}',
            'html': f'''
                <div>
                    <h2>Hello {product.seller.full_name},</h2>
                    <p>Your product has been successfully approved.</p>
                    <p><strong>Product name:</strong> {product.name_en}</p>
                    <p><strong>Product code:</strong> {product.product_code}</p>
                    <p>Please now ship the goods to our warehouse in Egypt.</p>
                    <br>
                    <p>The Wikala Team</p>
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
            'subject': f'Update on your product: {product.name_en}',
            'html': f'''
                <div>
                    <h2>Hello {product.seller.full_name},</h2>
                    <p>We're sorry to inform you that your product was not approved.</p>
                    <p><strong>Product name:</strong> {product.name_en}</p>
                    <p><strong>Reason:</strong> {product.rejection_reason}</p>
                    <p>You can edit the product and resubmit it.</p>
                    <br>
                    <p>The Wikala Team</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_shipment_updated(product, to_status):
    try:
        status_labels = {
            'in_warehouse_egypt': 'Arrived at Egypt warehouse',
            'in_transit': 'In transit to Germany',
            'in_warehouse_germany': 'Arrived at Germany warehouse — available for sale',
            'listed': 'Listed on the platform',
        }
        label = status_labels.get(to_status, to_status)
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': product.seller.user.email,
            'subject': f'Shipment update for your product: {product.name_en}',
            'html': f'''
                <div>
                    <h2>Hello {product.seller.full_name},</h2>
                    <p>The shipment status of your product has been updated.</p>
                    <p><strong>Product:</strong> {product.name_en}</p>
                    <p><strong>New status:</strong> {label}</p>
                    <br>
                    <p>The Wikala Team</p>
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
            'subject': f'Your statement for {statement.period_end} is ready',
            'html': f'''
                <div>
                    <h2>Hello {statement.seller.full_name},</h2>
                    <p>Your monthly statement is ready.</p>
                    <p><strong>Period:</strong> {statement.period_start} — {statement.period_end}</p>
                    <p><strong>Total sales:</strong> {statement.total_sales} EUR</p>
                    <p><strong>Net amount due to you:</strong> {statement.net_amount} EUR</p>
                    <p>The transfer will be made within 10 business days.</p>
                    <br>
                    <p>The Wikala Team</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


def send_shipment_request_accepted(shipment_request):
    try:
        items_html = ''.join([
            f'<tr><td>{item.product.name_en}</td><td>{item.product.product_code}</td><td>{item.cartons_count}</td><td>{item.total_units}</td></tr>'
            for item in shipment_request.items.all()
        ])

        delivery_methods = {
            'pickup': 'Pickup by Wikala',
            'courier': 'Courier company',
            'drop_off': 'Drop-off at Wikala location',
        }
        method_label = delivery_methods.get(shipment_request.delivery_method, shipment_request.delivery_method)

        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': shipment_request.seller.user.email,
            'subject': f'Shipment request {shipment_request.request_number} accepted ✅',
            'html': f'''
                <div>
                    <h2>Hello {shipment_request.seller.full_name},</h2>
                    <p>Your shipment request has been accepted.</p>
                    <p><strong>Request number:</strong> {shipment_request.request_number}</p>
                    <p><strong>Delivery date:</strong> {shipment_request.delivery_date}</p>
                    <p><strong>Delivery method:</strong> {method_label}</p>
                    {f'<p><strong>Notes:</strong> {shipment_request.delivery_notes}</p>' if shipment_request.delivery_notes else ''}
                    <br>
                    <h3>Products:</h3>
                    <table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
                        <tr>
                            <th>Product</th>
                            <th>Code</th>
                            <th>Cartons</th>
                            <th>Total units</th>
                        </tr>
                        {items_html}
                    </table>
                    <br>
                    <p>The Wikala Team</p>
                </div>
            '''
        })
    except Exception as e:
        print(f"Email error: {e}")


# ────────────────────────────────────────
# Widerruf (§ 356a BGB) — MUST stay in German (legal, German customers)
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