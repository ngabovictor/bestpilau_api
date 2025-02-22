from notifications.sms import send_sms_task
from orders.models import Order
from payments.fdi import FDIClient
import uuid
from payments.models import Transaction
from payments.serializers import TransactionSerializer
from notifications import push as push_notifications


fdi_client = FDIClient()


def initialize_payment(order: Order, payment_account_number: str, payment_method: str = 'MOBILE_MONEY', currency: str = 'RWF'):
    
    amount = float(order.total_amount)
    
    # Ensure payment account number starts with '07'
    if payment_account_number.startswith('250'):
        payment_account_number = '0' + payment_account_number[3:]
    elif not payment_account_number.startswith('07'):
        raise ValueError("Payment account number must start with '07' or '250'")
    
    transaction_id = str(uuid.uuid4())
    
    payload, response = fdi_client.initiate_payment(amount, transaction_id, {
        'msisdn': payment_account_number,
        'firstName': order.customer.first_name,
        'lastName': order.customer.last_name,
        'email': order.customer.email,
    })
    
    
    transaction_data = {
        'id': transaction_id,
        'status': 'PENDING',
        'amount': amount,
        'currency': currency,
        'order': order,
        'outlet': order.outlet,
        'gw_codename': 'fdi',
        'transaction_type': 'PAYMENT',
        'reference_id': response['transaction_id'],
        'payment_account_number': payment_account_number,
        'payment_method': payment_method,
        'gw_request_payload': payload,
        'gw_request_response': response,
        'created_by': order.created_by,
    }
    
    transaction = Transaction.objects.create(**transaction_data)
    
    if response['status'] != 'processing':
        transaction.status = 'FAILED'
        transaction.save()
        order.status = 'CANCELLED'
        order.cancelled_reason = f'Payment failed: {response["message"]}'
        order.save()



def handle_fdi_callback(data: dict):
    transaction_data = data.get('data', {})
    transaction_state = transaction_data.get('state')
    transaction_id = transaction_data.get('trxRef')
    reference_id = transaction_data.get('gwRef')
    
    # Get transaction by both reference_id and id
    transaction = Transaction.objects.filter(
        id=transaction_id,
        reference_id=reference_id
    ).first()
    
    if not transaction:
        return
        
    # Update transaction callback data
    transaction.gw_request_callback = data
    
    # Update transaction status based on payment state
    if transaction_state == 'successful':
        transaction.status = 'COMPLETED'
    else:
        transaction.status = 'FAILED'
        
    transaction.save()
    
    # Get associated order and update status
    order = transaction.order
    if order.status == 'PENDING':
        if transaction_state == 'successful':
            order.status = 'CONFIRMED'
            # Send notification to outlet worker/admins if order is confirmed
        
            message = f'New order received! Order ID: {order.reference_code}. Customer phone: {order.customer.username}. Please check the dashboard for details and prepare it promptly.'
            phone_numbers = [worker.username for worker in order.outlet.workers.all() if worker.username.startswith(('+250', '250', '07'))]
            
            if order.outlet.phone_number:
                phone_numbers.append(order.outlet.phone_number)
            
            send_sms_task(message=message, phone_numbers=phone_numbers)
            push_notifications.send_order_notification(order)
        else:
            order.status = 'CANCELLED'
            order.cancelled_reason = 'Payment failed: {}'.format(transaction_data.get('message', 'Unknown error'))
        order.save()
        
        
def verify_transaction(transaction: Transaction):
    response = fdi_client.check_payment_status(str(transaction.id))
    order = transaction.order
    
    if response['status'] == 'successful':
        transaction.status = 'COMPLETED'
        transaction.gw_request_callback = response
        transaction.save()
        order.status = 'CONFIRMED'
        order.save()
        
        # Send notification to outlet worker/admins if order is confirmed
        
        message = f'New order received! Order ID: {order.reference_code}. Customer phone: {order.customer.username}. Please check the dashboard for details and prepare it promptly.'
        phone_numbers = [worker.username for worker in order.outlet.workers.all() if worker.username.startswith(('+250', '250', '07'))]
        
        if order.outlet.phone_number:
            phone_numbers.append(order.outlet.phone_number)
        
        send_sms_task(message=message, phone_numbers=phone_numbers)
        
    elif response['status'] == 'fail':
        transaction.status = 'FAILED'
        transaction.gw_request_callback = response
        transaction.save()
        order.status = 'CANCELLED'
        order.cancelled_reason = 'Payment failed: {}'.format(response['channel_message'])
        order.save()
        
        # Revert coupon used
        
        coupon = order.coupon
        
        if coupon:
            coupon.uses = int(coupon.uses) - 1
            coupon.save()
        
    return transaction
