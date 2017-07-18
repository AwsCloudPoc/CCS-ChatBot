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

def terminate_instances(intent_request):
    print get_slots(intent_request)
    user = get_slots(intent_request)["D_User"]
    print user
    TagName = get_slots(intent_request)["D_TagName"]
    print TagName
    InstanceId = get_slots(intent_request)["D_InstanceId"]
    print InstanceId
    source = intent_request['invocationSource']
    session_attributes = intent_request['sessionAttributes']

    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)
        output_session_attributes = intent_request['sessionAttributes']

        return delegate(output_session_attributes, get_slots(intent_request))

def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']
	
    if intent_name == 'TerminateInstance':
        return terminate_instances(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):

    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
