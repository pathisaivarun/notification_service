import base64
from email.message import EmailMessage
import os.path
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv

#This class will send mails
class MailService(): 

    def __init__(self):
        self.set_mail_template()
        load_dotenv()
        #Here, we are connecting our google oauth credentials to google to send the mails
        self.scopes = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.addons.current.action.compose", "https://www.googleapis.com/auth/gmail.send"]
        creds = None
        if os.path.exists(os.getenv("GOOGLE_MAIL_TOKEN_PATH")):
            creds = Credentials.from_authorized_user_file(os.getenv("GOOGLE_MAIL_TOKEN_PATH"), self.scopes)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        os.getenv("GOOGLE_MAIL_CREDENTIALS_PATH"), self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                with open(os.getenv("GOOGLE_MAIL_TOKEN_PATH"), "w") as token:
                    token.write(creds.to_json())
        self.creds = creds

    def set_mail_template(self):
        self.subject = "Your order has been "
        self.body = "Hello user_name,\n\nYour order has been "

    def send_notification(self, record):
        try:
            service = build("gmail", "v1", credentials=self.creds)
            message = EmailMessage()

            #Below block will form the mail body and subject
            body = self.body.replace("user_name", record["user_name"])
            body = body + record["message"]
            for order_id in record["orders_meta_info"].keys():
                order_details = record["orders_meta_info"][order_id]
                order_details_for_body = "\n\nId: {}\nOrder placed on: {}\nQuantity: {}\nTotal cost: {}".format(order_id, order_details['placed_on'], order_details['quantity'], order_details['total_cost'])
                body = body + order_details_for_body

            message.set_content(body)

            message["To"] = record["email"]
            message["From"] = "saivarunn150205@gmail.com"
            message["Subject"] = self.subject + record["message"]

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
        return False

if __name__ == "__main__":
    obj = MailService()
    print(obj.send_notification({"notification_service": "mail", "message": "shipped", "notification_id": 1234, "email": "saivarunn150205@gmail.com", "orders_meta_info": {"1234": {"placed_on": "2024-01-01 12:00:00", "total_cost": 100, "quantity": 2}, "1235": {"placed_on": "2024-01-01 12:00:00", "total_cost": 100, "quantity": 1}}, "items": 2, "user_name": "sai varun"}))
