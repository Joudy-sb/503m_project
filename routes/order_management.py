# --------------------------------Order Management System ----------------------------
from datetime import datetime
from io import BytesIO
from flask import send_file, Blueprint
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from flask import jsonify, request
from database import Order, OrderItem, Customer, Product, Return, db
from flask_jwt_extended import jwt_required, get_jwt_identity

order_management = Blueprint('order_management', __name__)


@order_management.route('/orders', methods=['GET']) #manage orders -> gets all orders from the db 
@jwt_required()
# MUST AUTHENTICATE ADMIN FIRST
def manage_orders():
    status = request.args.get('status')  # Get the status filter from the query params
    
    # Query orders based on the status filter, if provided
    if status:
        orders = Order.query.filter_by(status=status).all()  # Filter orders by status
    else:
        orders = Order.query.all()  # Get all orders if no filter is applied
    
    # Prepare the orders data for JSON response
    orders_data = []
    for order in orders:
        order_data = {
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'status': order.status,
            'total_price': order.total_price,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else None,
        }
        
        orders_data.append(order_data)

    # Return the orders data as a JSON response
    return jsonify(orders_data)

@order_management.route('/orderitems', methods=['GET']) #manage orders -> gets all order items from the db 
# MUST AUTHENTICATE ADMIN FIRST
def get_order_items():
    # Query all OrderItems from the database
    order_items = OrderItem.query.all()
    
    # Format each OrderItem as a dictionary
    order_items_list = [
        {
            "order_item_id": item.order_item_id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_purchase": item.price_at_purchase
        }
        for item in order_items
    ]
    
    # Return the list of order items as JSON
    return jsonify(order_items_list)

@order_management.route('/order/status/<int:order_id>', methods=['GET']) # Track order status
# MUST AUTHENTICATE ADMIN FIRST
def get_order_status(order_id):
    # Query the Order by the given order_id
    order = Order.query.get(order_id)
    
    # Check if the order exists
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    
    # Return the order status in JSON format
    return jsonify({
        "order_id": order.order_id,
        "status": order.status
    })

@order_management.route('/order/<int:order_id>/invoice', methods=['GET']) # MAKE THIS SECURE!!!
def generate_invoice(order_id):
    # Query the Order by the given order_id
    order = Order.query.get(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404

    # Fetch associated customer and order items
    customer = Customer.query.get(order.customer_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    # Create a PDF in memory
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    # Basic Invoice Layout
    pdf.setTitle(f"Invoice_{order_id}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, height - 100, f"Invoice for Order #{order_id}")
    pdf.setFont("Helvetica", 12)

    # Customer Information
    pdf.drawString(50, height - 150, f"Customer: {customer.name}")
    pdf.drawString(50, height - 170, f"Email: {customer.email}")
    pdf.drawString(50, height - 190, f"Address: {customer.address}")
    pdf.drawString(50, height - 210, f"Phone: {customer.phone}")

    # Order Information
    pdf.drawString(50, height - 250, f"Order Date: {order.created_at.strftime('%Y-%m-%d')}")
    pdf.drawString(50, height - 270, f"Status: {order.status}")
    pdf.drawString(50, height - 290, f"Total Price: ${order.total_price:.2f}")

    # Table of Ordered Items
    data = [["Product ID", "Quantity", "Price at Purchase", "Total Price"]]
    for item in order_items:
        product = Product.query.get(item.product_id)
        data.append([
            item.product_id,
            item.quantity,
            f"${item.price_at_purchase:.2f}",
            f"${item.quantity * item.price_at_purchase:.2f}"
        ])
    
    # Add the order items table to the PDF
    table = Table(data, colWidths=[100, 100, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - 400)

    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    # Send the PDF as a file to download
    return send_file(pdf_buffer, as_attachment=True, download_name=f"Invoice_Order_{order_id}.pdf", mimetype='order_managementlication/pdf')

ALLOWED_ORDER_STATUSES = {"Pending", "Processing", "Shipped", "Delivered"}


@order_management.route('/update-order-status/<int:order_id>', methods=['PUT'])    # admin can update the status of the order 
                                                                            # validated admin input
#AUTHENTICATION!!
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")

    # Check if the status provided is valid
    if new_status not in ALLOWED_ORDER_STATUSES:
        return jsonify({"error": "Invalid status. Allowed values are 'pending', 'processing', 'shipped', 'delivered'"}), 400

    # Fetch the order from the database
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Update the order status
    order.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Order status updated successfully",
        "order_id": order.order_id,
        "new_status": order.status
    }), 200

@order_management.route('/returns', methods=['GET']) # view return requests
def view_returns():
    status = request.args.get("status")
    if status:
        returns = Return.query.filter_by(status=status).all()
    else:
        returns = Return.query.all()
        
    return jsonify([{
        "return_id": r.return_id,
        "order_id": r.order_id,
        "product_id": r.product_id,
        "status": r.status,
        "reason": r.reason,
        "action": r.action,
        "requested_at": r.requested_at,
        "processed_at": r.processed_at
    } for r in returns])

@order_management.route('/returns/<int:return_id>/process', methods=['POST']) # process return request
def process_return(return_id):
    # Get the return request from the database
    return_request = Return.query.get_or_404(return_id)

    # Ensure the action is either Refund or Replacement
    action = request.json.get('action', None)
    status = request.json.get('status', None)
    
    #validation
    if not action or action not in ['Refund', 'Replacement']:
        return jsonify({"error": "Invalid action. Action must be 'Refund' or 'Replacement'."}), 400
    
    if not status or status not in ['Approved', 'Rejected']:
        return jsonify({"error": "Invalid status. Status must be 'Approved' or 'Rejected'."}), 400

    # Update the return request based on action and status
    return_request.status = status
    return_request.action = action
    return_request.processed_at = datetime.utcnow()

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        'message': 'Return request processed successfully.',
        'return_id': return_request.return_id,
        'status': return_request.status,
        'action': return_request.action,
        'processed_at': return_request.processed_at
    }), 200
