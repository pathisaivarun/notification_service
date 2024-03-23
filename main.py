#imporing required modules
import sys
from service_modules.mail_module import MailService as mail_service
from rabbitmq_wrapper import RabbitMQWrapper

class RunNotificationServices():
    
    #In this method, we have to tell which service we are going to use to send the notification
    def __init__(self, notification_service, records_limit):
        if not notification_service:
            print("notification service not found")
            return

        self.notification_service = notification_service
        self.records_limit = records_limit
        #Below, we are creating the service specific queue connection with rabbitmq
        self.queue_conn = RabbitMQWrapper(notification_service)
        if not self.queue_conn:
            print("Failed to connect rabbitmq")
        else:
            print("Successfully connected to rabbitmq queue")


    #This method will connect to the required notification service module like gmail, sms, and etc
    def connect_to_required_module(self):
        curr_attempt = 0
        while True:
            try:
                #We are connecting to the required notification service here
                #we can add some more services with the if else condition
                if self.notification_service == "mail_notification":
                    self.service_conn = mail_service()
            except Exception as e:
                curr_attempt += 1
                if curr_attempt < 2:
                    continue
                print("Error while connecting to {} service, msg: {}".format(self.notification_service, e))
                self.service_conn = None
            break

    #This method will pop the records from queue and sends the notification
    def pop_and_process_data_from_queue(self):
        if not self.notification_service:
            print("Notification service not found")
            return

        self.connect_to_required_module()
        if not self.service_conn:
            return

        #Here, we are popping the records from queue and sending notification
        for ind in range(0, self.records_limit):
            popped_record = self.queue_conn.pop()
            if popped_record is None:
                print("No messages found")
                break
            status = self.service_conn.send_notification(popped_record)
            if not status:
                self.send_record_to_failed_queue(popped_record)
            else:
                print("Successfully sent the notification, id: {}".format(popped_record["notification_id"]))
        return
    
    def send_record_to_failed_queue(self, popped_record):
        if not self.failed_queue_conn:
            self.failed_queue_conn = RabbitMQWrapper(f"{notification_service}_failed")
        self.failed_queue_conn.push(popped_record)

def parse_args(args_list):
    if type(args_list).__name__ == "list" and len(args_list) == 3:
        return args_list[1], args_list[2]

if __name__ == "__main__":
    notification_service, records_limit = parse_args(sys.argv)
    if notification_service:
        obj = RunNotificationServices(notification_service, int(records_limit))
        obj.pop_and_process_data_from_queue()
