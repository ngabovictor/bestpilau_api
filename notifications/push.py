from .onesignal import OneSignalClient, Notification

onesignal_client = OneSignalClient()

def send_workers_order_notification(order):
    notification = Notification()

    notification.set_attribute('contents', {
        'en': f"You have received a new order #{order.reference_code}, from {order.customer.username}. Open it and process it as fast as possible 👀"
    })
    notification.set_attribute('headings', {
        'en': "New incoming order 👏"
    })
    
    notification.set_attribute('buttons', [
        {
            'id': 'view_order',
            'text': 'View Order'
        },
        {
            'id': 'start_processing',
            'text': 'Start Processing'
        },  
    ])

    notification.set_attribute('is_android', True)
    
    notification.set_attribute('included_segments', [
        "Outlet users"
    ])
    
    outlet_users = order.outlet.workers.all()
    
    notification.set_attribute('included_external_ids', [
        user.username for user in outlet_users
    ])
    
    notification.set_attribute('data', {
        'order_id': str(order.id),
        'outlet_id': str(order.outlet.id),
        'customer_id': str(order.customer.id),
    })

    response = onesignal_client.send_notification(notification)

    print(response)


def send_push_notification(subject: str, message: str, recipients: list, actions: list = [], data: dict = {}):
    notification = Notification()

    notification.set_attribute('contents', {
        'en': message
    })
    notification.set_attribute('headings', {
        'en': subject
    })
    
    notification.set_attribute('buttons', actions)

    notification.set_attribute('is_android', True)
    notification.set_attribute('is_ios', True)
    
    notification.set_attribute('included_external_ids', recipients)
    notification.set_attribute('included_segments', [
        "Total Subscriptions"
    ])
    
    notification.set_attribute('data', data)

    response = onesignal_client.send_notification(notification)

    print(response)