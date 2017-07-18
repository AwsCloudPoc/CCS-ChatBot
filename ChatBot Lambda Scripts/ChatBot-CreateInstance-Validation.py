import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_create_instances(user, os_type, region, port):
    os_types = ['AmazonLinux', 'RHEL7.3', 'Windows2016Base']
    if os_type is not None and os_type not in os_types:
	    return build_validation_result(False,
									   'OsType',
                                       'We do not have {}, would you like a different type of os?  '.format(os_type))
									   
    regions = ['us-east-1', 'us-west-2', 'ap-south-1']
    if region is not None and region not in regions:
         return build_validation_result(False,
									   'Region',
                                       'We do not have {}, would you like a different region?  '.format(region))
    
    ports = ['80', '22', '3389','443']
    if port is not None and port not in ports:
         return build_validation_result(False,
									   'Port',
                                       'We do not have {}, would you like a different port?  '.format(port))
    
    return build_validation_result(True, None, None)

def create_instances(intent_request):
    user = get_slots(intent_request)["User"]
    email = get_slots(intent_request)["Email"]
    os_type = get_slots(intent_request)["OsType"]
    region = get_slots(intent_request)["Region"]
    port = get_slots(intent_request)["Port"]
    TagName = get_slots(intent_request)["TagName"]
    source = intent_request['invocationSource']
    session_attributes = intent_request['sessionAttributes']

    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_create_instances(user, os_type, region, port)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes']

        return delegate(output_session_attributes, get_slots(intent_request))

def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'CreateInstance':
        return create_instances(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    print event
    print context
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
