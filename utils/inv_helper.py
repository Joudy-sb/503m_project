
from flask_mail import Mail, Message
from database import Product
from flask import current_app as app
mail = Mail()
def check_and_notify_low_stock(product_id):
    """
    Check if a product's stock is below the threshold and notify admins.
    """
    LOW_STOCK_THRESHOLD = 10  # Set your low stock threshold
    product = Product.query.get(product_id)

    if product and product.stock_level < LOW_STOCK_THRESHOLD:
        # Compose email
        subject = f"Low Stock Alert: {product.name}"
        body = f"""
        The stock level for the product '{product.name}' (ID: {product.product_id}) 
        has fallen below the threshold of {LOW_STOCK_THRESHOLD}.
        
        Current Stock: {product.stock_level}
        Warehouse: {product.warehouse_location}
        """

        # Send email to admins
        recipients = ["antoinesaade117@gmail.com"]  # Replace with admin emails
        send_email(subject, body, recipients)

def send_email(subject, body, recipients):
    """
    Send an email notification.
    """
    try:
        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=recipients,
                body=body
            )
            mail.send(msg)
            print(f"Email sent successfully")
    except Exception as e:
        print(f"Failed to send email : {str(e)}")
