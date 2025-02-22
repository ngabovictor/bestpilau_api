import os
import requests


NOTIFICATION_ONESIGNAL_APP_ID = os.getenv("NOTIFICATION_ONESIGNAL_APP_ID")
NOTIFICATION_ONESIGNAL_APP_KEY = os.getenv("NOTIFICATION_ONESIGNAL_APP_KEY")


class OneSignalClient:
    def __init__(self):
        self.app_id = NOTIFICATION_ONESIGNAL_APP_ID
        self.app_key = NOTIFICATION_ONESIGNAL_APP_KEY

    def send_notification(self, notification):
        """Send a notification via OneSignal API"""
        url = "https://api.onesignal.com/notifications?c=push"
        headers = {
            "Authorization": f"{self.app_key}",
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        payload = notification.to_dict()
        payload['app_id'] = self.app_id

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

