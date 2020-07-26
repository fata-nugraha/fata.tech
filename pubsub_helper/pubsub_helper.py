from google.cloud import pubsub
from google.oauth2 import service_account
import os

def publish(data):
    SERVICE_ACCOUNT_FILE = 'pubsubcred.json'
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE)
    project_id = os.environ.get("PROJECT")
    topic_id = os.environ.get("TOPIC")
    publisher = pubsub.PublisherClient(credentials=credentials)
    topic_path = publisher.topic_path(project_id, topic_id)
    publisher.publish(
        topic_path, data=data.encode("utf-8")  # data must be a bytestring.
    )