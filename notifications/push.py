import os
import uuid

import onesignal
from onesignal.api import default_api

from orders.models import Order

# See configuration.py for a list of all supported configuration parameters.
# Some of the OneSignal endpoints require USER_KEY bearer token for authorization as long as others require APP_KEY
# (also knows as REST_API_KEY). We recommend adding both of them in the configuration page so that you will not need
# to figure it yourself.
configuration = onesignal.Configuration(
    app_key = "NOTIFICATION_ONESIGNAL_APP_KEY",
    user_key = "NOTIFICATION_ONESIGNAL_USER_KEY"
)

NOTIFICATION_ONESIGNAL_APP_ID = os.getenv("NOTIFICATION_ONESIGNAL_APP_ID")


# Enter a context with an instance of the API client
with onesignal.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = default_api.DefaultApi(api_client)
    

def send_order_notification(order: Order):
    notification = onesignal.Notification()
    notification.set_attribute('app_id', NOTIFICATION_ONESIGNAL_APP_ID)
    notification.set_attribute('external_id', str(uuid.uuid4()))
    notification.set_attribute('is_android', True)
    contentsStringMap = onesignal.StringMap()   
    headingStringMap = onesignal.StringMap()   
    headingStringMap.set_attribute('en', "New incoming order 👏")
    contentsStringMap.set_attribute('en', f"You have received a new order #{order.reference_code}. Open it and process it as fast as possible 👀")
    notification.set_attribute('contents', contentsStringMap)
    notification.set_attribute('headings', headingStringMap)
    outlet_users = order.outlet.workers.all()
    notification.set_attribute('include_external_user_ids', [user.username for user in outlet_users])

    notificationResponse = api_instance.create_notification(notification)
