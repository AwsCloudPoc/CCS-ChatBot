import boto3
import logging
import decimal
import json
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):

    UserSelected = event['currentIntent']['slots']['D_User']
    TagName = event['currentIntent']['slots']['D_TagName']
    InstanceIdSelected = event['currentIntent']['slots']['D_InstanceId']
    
    client = boto3.resource('ec2', region_name= 'us-east-1')
    ec2 = boto3.client('ec2', region_name= 'us-east-1')
    dynamodb = boto3.resource('dynamodb')
    
    table_instance = dynamodb.Table('instanceiddetails')
	
    instance_response = table_instance.query(
        KeyConditionExpression=Key('instanceid').eq(InstanceIdSelected)
    ) 
    
    user = instance_response["Items"][0]["username"]

    tag_name = instance_response["Items"][0]["tagname"]

    instance_id = instance_response["Items"][0]["instanceid"]

    sg_id = instance_response["Items"][0]["sec_grp_id"]

	
    if (tag_name == TagName and user == UserSelected):
        response = ec2.terminate_instances(
            InstanceIds=[
				instance_id,
			],
		)

    return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {
                "contentType": "PlainText",
                "content": "Your request to terminate instance is accepted. You will receive an email shortly"
                }}}
