import boto3
import logging
import json
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):

    EventType = event['currentIntent']['slots']['S_Event']
    UserSelected = event['currentIntent']['slots']['S_User']
    TagName = event['currentIntent']['slots']['S_TagName']
    InstanceIdSelected = event['currentIntent']['slots']['S_InstanceId']
	
    ec2 = boto3.client('ec2', region_name= 'us-east-1')
	
    status = ec2.describe_instances(InstanceIds=[InstanceIdSelected])
	
    if EventType == "Start":
        instance_state = status["Reservations"][0]["Instances"][0]["State"]["Name"]
		
        if instance_state == "stopped":
            response = ec2.start_instances(InstanceIds=[InstanceIdSelected])
            return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {
                "contentType": "PlainText",
                "content": "Your request to start an instance has been accepted. You will receive an email shortly."
                }}}
        else:
		
			return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {
                "contentType": "PlainText",
                "content": "Your Server is already running."
                }}}
			
    else:
        instance_state = status["Reservations"][0]["Instances"][0]["State"]["Name"]
        print instance_state
		
        if instance_state == "running":
            response = ec2.stop_instances(InstanceIds=[InstanceIdSelected])
            return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {
                "contentType": "PlainText",
                "content": "Your request to stop an instance has been accepted. You will receive an email shortly."
                }}}	
        else:
			return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {
                "contentType": "PlainText",
                "content": "Your Server is already stopped."
                }}}
