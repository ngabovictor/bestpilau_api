from orders.models import Order
from payments.fdi import FDIClient
import uuid
from payments.models import Transaction
from payments.serializers import TransactionSerializer


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
    reference_id = transaction_data.get('trxRef')
    
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
        else:
            order.status = 'CANCELLED'
            order.cancelled_reason = 'Payment failed: {}'.format(transaction_data.get('message', 'Unknown error'))
        order.save()
