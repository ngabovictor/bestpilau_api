
import os


def send_sms_task(message, phone_numbers, sender_id=None):
    """
    :param list[str] phone_numbers: Recipient phone numbers (should not start with a +)
    :param str message: SMS Message to be sent
    :param str sender: Custom SenderID/Name
    """

    print("Sending SMS message")
    print(message)
    print(phone_numbers)

    try:
        local_numbers = []
        international_numbers = []
        for phone_number in phone_numbers:
            if phone_number.startswith("+250"):
                local_numbers.append(phone_number)
            else:
                international_numbers.append(phone_number)

        if len(local_numbers) > 0:
            if not sender_id:
                pass

        if len(international_numbers) > 0:
            print("Sending sms to international phone numbers")
    except Exception as e:
        print(str(e))
