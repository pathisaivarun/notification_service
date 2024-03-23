Goal: Here, we need a create a way to send notifications through different types of services like mail, sms, whatsapp sms and etc.

Design:
To achieve this, we created a small design using rabbitmq, python scripts, google mail service
1) Intially, the notifications should be pushed to queues in rabbitmq.
2) Each notification service will have an individual queue. Like for mail -> mail_notification, sms -> sms_notification and etc.
3) Our approach is to do batch processing using python scripts
4) Once we will run the python script with arguments like which service we want to use, how many messages we want to process
5) The python script will take the arguments and send notifications for that batch of records

main.py is the main python script
Example on how to use it:
cmd: python3 main.py mail_notification 100
Above command will process 100 records from queue and sends mail notifications
