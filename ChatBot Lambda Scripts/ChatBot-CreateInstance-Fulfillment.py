import boto3
import logging
import decimal
import json
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    print(event)
    UserSelected = event['currentIntent']['slots']['User']
    EmailSelected = event['currentIntent']['slots']['Email']
    OsTypeSelected = event['currentIntent']['slots']['OsType']
    regionSelected = event['currentIntent']['slots']['Region']
    PortSelected =  event['currentIntent']['slots']['Port']
    TagName = event['currentIntent']['slots']['TagName']

    client = boto3.resource('ec2', region_name= regionSelected)
    ec2 = boto3.client('ec2', region_name= regionSelected)
    dynamodb = boto3.resource('dynamodb')
    
    table_region = dynamodb.Table('region_details')
    
    region_response = table_region.query(
      KeyConditionExpression=Key('region').eq(regionSelected)
    ) 
    
    subnet = region_response["Items"][0]["subnet_id"]

    az = region_response["Items"][0]["AZ"]

    table_ami_type = dynamodb.Table('amidetails')
    
    ami_type = table_ami_type.query(
      KeyConditionExpression=Key('OsType').eq(OsTypeSelected)
    ) 
    
    Image_Id = ami_type["Items"][0]["ImageId"]

    instance_type = ami_type["Items"][0]["instance_type"]

    ec2_sg = boto3.client('ec2')
    
    response_sg = ec2_sg.create_security_group(
       Description= TagName + '-SG',
       GroupName= TagName + '-SG',
       VpcId='vpc-5b68aa3e'  
    )
    
    sg_id = response_sg['GroupId']

    response_sgigress = ec2_sg.authorize_security_group_ingress(
    GroupId= sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': int(PortSelected, 10),
            'ToPort': int(PortSelected, 10),
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }]}
    ]) 


    table = dynamodb.Table('instanceiddetails')
	
    response = ec2.run_instances(
    ImageId= Image_Id,
    InstanceType= instance_type,
    KeyName='ChatBot',
    MaxCount=1,
    MinCount=1,
    Placement={
        'AvailabilityZone': az
    },
    
    NetworkInterfaces=[
        {
            'AssociatePublicIpAddress': True,
            'DeviceIndex': 0,
            'Groups': [sg_id],
			'SubnetId': subnet
        },
    ],
  
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': TagName
                },
                {
                    'Key': 'EmailID',
                    'Value': EmailSelected
                },
            ]
        },
    ]
)

    instance_id = response["Instances"][0]["InstanceId"]

    table.put_item(
    Item={
        'username': '{}'.format(UserSelected),
        'instanceid': '{}'.format(instance_id),
		'emailid': '{}'.format(EmailSelected),
		'tagname': '{}'.format(TagName),
		'sec_grp_id':'{}'.format(sg_id)
    }
)

    inst_state = ec2.describe_instances(
    InstanceIds=[
        instance_id
    ]
    )

    state = inst_state["Reservations"][0]["Instances"][0]["State"]["Name"]

    return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {
                "contentType": "PlainText",
                "content": "Your request to provision a server is accepted. You will receive an email shortly."
                }}}
