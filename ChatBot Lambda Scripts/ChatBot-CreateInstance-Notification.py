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
    
    if event["detail"]["state"] == "running":
    
        instance_id = event["detail"]["instance-id"]

        tag_details = conn.describe_instances(InstanceIds=[instance_id])

        if tag_details["Reservations"][0]["Instances"][0]["Tags"][0]["Key"] == "Name":
            server_name = tag_details["Reservations"][0]["Instances"][0]["Tags"][0]["Value"]
            email_id = tag_details["Reservations"][0]["Instances"][0]["Tags"][1]["Value"]
        else:
            server_name = tag_details["Reservations"][0]["Instances"][0]["Tags"][1]["Value"]
            email_id = tag_details["Reservations"][0]["Instances"][0]["Tags"][0]["Value"]
            
        server_ip = tag_details["Reservations"][0]["Instances"][0]["PublicIpAddress"]
		
    ses = boto3.client('ses')

    emailfrom = 'awslexchatbot@gmail.com'
    emailto = email_id
    emailcc = 'awslexchatbot@gmail.com'
    emaiLsubject = 'ChatBot Notification'
    emailbody = 'Hi User,\n \nYour server'+ ' '  + server_name +  ' ' +'is up and running. \n'+ 'Your instance ID is ' + instance_id + '.\nYour Public IP Address is ' + server_ip + '.\n' +'Please check after 10 minutes. \n \n' + 'Thank you'
	
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
    
