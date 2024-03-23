import pika
import json

#This script will help us in connecting to rabbitmq queues, pushing and popping the messages from the queues
class RabbitMQWrapper():
    def __init__(self, queue):
        self.queue = queue
        self.connect_to_queue()

    #Here, we are creating the channel and connecting to a specific queue
    def connect_to_queue(self):
        curr_attempts = 0
        self.connection, self.channel = None, None
        while True:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                self.channel = self.connection.channel()
                self.channel.exchange_declare('notification_service')
                self.channel.queue_declare(self.queue)
                self.channel.queue_bind(self.queue, exchange= 'notification_service')
                print("connection created")
            except Exception as e:
                curr_attempts += 1
                if curr_attempts < 2:
                    continue
                print(f"Failed in connecting to rabbitmq queue, error: #{e}")
            break

    #This method pushes the record to queue 
    def push(self, message):
        if not self.channel:
            self.connect_to_queue()

        if not self.channel:
            return

        curr_attempts = 0
        while True:
            try:
                self.channel.basic_publish(exchange= 'notification_service', routing_key = self.queue, body = json.dumps(message))
            except Exception as e:
                curr_attempts += 1
                if curr_attempts < 2:
                    continue
                print(f"Failed in connecting to rabbitmq queue, error: #{e}")
                return False
            break
        return True

    #This method pops the message from queue and returns it
    #And also deletes the message from queue permanently
    def pop(self):
        if not self.channel:
            self.connect_to_queue()

        if not self.channel:
            return

        message = None
        curr_attempts = 0
        while curr_attempts < 2:
            try:
                method_frame, header_frame, body = self.channel.basic_get(queue = self.queue)        
                if method_frame is None or method_frame.NAME == 'Basic.GetEmpty':
                    return None
                else:            
                    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            except Exception as e:
                curr_attempts += 1
                if curr_attempts > 2:
                    print(f"Failed in connecting to rabbitmq queue, error: #{e}")
                    break
                continue
            break
        return json.loads(body.decode("utf-8"))

    def close(self):
        if self.connection:
            self.channel.close()
            self.connection.close()

