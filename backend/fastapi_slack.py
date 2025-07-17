import os
import requests

def send_slack_alert(message: str):
    slack_url = os.getenv("SLACK_WEBHOOK_URL")

    if not slack_url:
        print("Slack webhook URL not configured.")
        return


    payload = {
        "text": message
    }

    try:
        response = requests.post(slack_url, json=payload)
        response.raise_for_status()
        print("Slack alert sent succefully!")
    except requests.RequestException as e:
        print("Eroor sending Slack alert:", e)