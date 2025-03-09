import os
import requests




class OneSignalClient:
    def __init__(self):
        self.ONESIGNAL_APPS = {
            'RIDERS': {
                'app_id': os.getenv("NOTIFICATION_ONESIGNAL_RIDERS_APP_ID"),
                'app_key': os.getenv("NOTIFICATION_ONESIGNAL_RIDERS_APP_KEY")
            },
            'CUSTOMERS': {
                'app_id': os.getenv("NOTIFICATION_ONESIGNAL_CUSTOMERS_APP_ID"),
                'app_key': os.getenv("NOTIFICATION_ONESIGNAL_CUSTOMERS_APP_KEY")
            },
            'WORKERS': {
                'app_id': os.getenv("NOTIFICATION_ONESIGNAL_WORKERS_APP_ID"),
                'app_key': os.getenv("NOTIFICATION_ONESIGNAL_WORKERS_APP_KEY")
            }
        }

    def send_notification(self, notification, app_name):
        """Send a notification via OneSignal API"""
        url = "https://api.onesignal.com/notifications?c=push"
        headers = {
            "Authorization": f"{self.ONESIGNAL_APPS[app_name]['app_key']}",
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        payload = notification.to_dict()
        payload['app_id'] = self.ONESIGNAL_APPS[app_name]['app_id']

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        return response.json()




class Notification:
    def __init__(self):
        self._attributes = {}

    def set_attribute(self, key, value):
        self._attributes[key] = value

    def to_dict(self):
        return self._attributes

