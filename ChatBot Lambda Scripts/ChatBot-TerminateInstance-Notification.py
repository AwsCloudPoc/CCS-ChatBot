import boto3
import gzip
import base64
import json
import urllib
from StringIO import StringIO
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):

    print("Received event: " + json.dumps(event, indent=5))
    
    conn = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    
    if event["region"] == "us-east-1":
    
    if event["detail"]["state"] == "terminated":
    
        instance_id = event["detail"]["instance-id"]

        dynamodb = boto3.resource('dynamodb')
    
        table_instance = dynamodb.Table('instanceiddetails')
	
        instance_response = table_instance.query(
            KeyConditionExpression=Key('instanceid').eq(instance_id)
        ) 

        user = instance_response["Items"][0]["username"]

        server_name = instance_response["Items"][0]["tagname"]

        email_id = instance_response["Items"][0]["emailid"]

        sec_group = instance_response["Items"][0]["sec_grp_id"]
        
        response = conn.delete_security_group(
            GroupId= sec_group
        )
    
        ses = boto3.client('ses')

        emailfrom = 'awslexchatbot@gmail.com'
        emailto = email_id
        emailcc = 'awslexchatbot@gmail.com'
        emaiLsubject = 'ChatBot Notification'
        emailbody = 'Hi ' + user + ',\n\nYour server'+ ' '  + server_name +  ' with instance ID ' + instance_id + ' is successfully terminated.\n\n' 'Thank you'
	
        response = ses.send_email(
            Source =emailfrom,
            Destination={
                'ToAddresses': [
                    emailto,
                ],
                'CcAddresses': [
                    emailcc,
                ]
            },
            Message={
                'Subject': {
                    'Data': emaiLsubject
                },
                'Body': {
                    'Text': {
                        'Data': emailbody
                    }
                }
            }
        )