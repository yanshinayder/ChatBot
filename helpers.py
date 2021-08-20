#
# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import boto3
import time
import logging
import json
import pprint
import os
import config as help_desk_config


logger = logging.getLogger()
logger.setLevel(logging.INFO)

kendra_client = boto3.client('kendra')

def get_slot_values(slot_values, intent_request):
    if slot_values is None:
        slot_values = {key: None for key in help_desk_config.SLOT_CONFIG}
    
    slots = intent_request['currentIntent']['slots']

    for key,config in help_desk_config.SLOT_CONFIG.items():
        slot_values[key] = slots.get(key)
        logger.debug('<<help_desk_bot>> retrieving slot value for %s = %s', key, slot_values[key])
        if slot_values[key]:
            if config.get('type', help_desk_config.ORIGINAL_VALUE) == help_desk_config.TOP_RESOLUTION:
                # get the resolved slot name of what the user said/typed
                if len(intent_request['currentIntent']['slotDetails'][key]['resolutions']) > 0:
                    slot_values[key] = intent_request['currentIntent']['slotDetails'][key]['resolutions'][0]['value']
                else:
                    errorMsg = help_desk_config.SLOT_CONFIG[key].get('error', 'Sorry, I don\'t understand "{}".')
                    raise help_desk_config.SlotError(errorMsg.format(slots.get(key)))
                
    return slot_values


def get_remembered_slot_values(slot_values, session_attributes):
    logger.debug('<<help_desk_bot>> get_remembered_slot_values() - session_attributes: %s', session_attributes)

    str = session_attributes.get('rememberedSlots')
    remembered_slot_values = json.loads(str) if str is not None else {key: None for key in help_desk_config.SLOT_CONFIG}
    
    if slot_values is None:
        slot_values = {key: None for key in help_desk_config.SLOT_CONFIG}
    
    for key,config in help_desk_config.SLOT_CONFIG.items():
        if config.get('remember', False):
            logger.debug('<<help_desk_bot>> get_remembered_slot_values() - slot_values[%s] = %s', key, slot_values.get(key))
            logger.debug('<<help_desk_bot>> get_remembered_slot_values() - remembered_slot_values[%s] = %s', key, remembered_slot_values.get(key))
            if slot_values.get(key) is None:
                slot_values[key] = remembered_slot_values.get(key)
                
    return slot_values


def remember_slot_values(slot_values, session_attributes):
    if slot_values is None:
        slot_values = {key: None for key,config in help_desk_config.SLOT_CONFIG.items() if config['remember']}
    session_attributes['rememberedSlots'] = json.dumps(slot_values)
    logger.debug('<<help_desk_bot>> Storing updated slot values: %s', slot_values)           
    return slot_values


def get_latest_slot_values(intent_request, session_attributes):
    slot_values = session_attributes.get('slot_values')
    
    try:
        slot_values = get_slot_values(slot_values, intent_request)
    except config.SlotError as err:
        raise help_desk_config.SlotError(err)

    logger.debug('<<help_desk_bot>> "get_latest_slot_values(): slot_values: %s', slot_values)

    slot_values = get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<help_desk_bot>> "get_latest_slot_values(): slot_values after get_remembered_slot_values: %s', slot_values)
    
    remember_slot_values(slot_values, session_attributes)
    
    return slot_values


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    logger.info('<<help_desk_bot>> "Lambda fulfillment function response = \n' + pprint.pformat(response, indent=4)) 

    return response


def increment_counter(session_attributes, counter):
    counter_value = session_attributes.get(counter, '0')

    if counter_value: count = int(counter_value) + 1
    else: count = 1
    
    session_attributes[counter] = count

    return count


def get_kendra_answer(question):
    try:
        KENDRA_INDEX = os.environ['KENDRA_INDEX']
    except KeyError:
        return 'Configuration error - please set the Kendra index ID in the environment variable KENDRA_INDEX.'
    
    try:
        response = kendra_client.query(IndexId=KENDRA_INDEX, QueryText=question)
    except:
        return None

    logger.debug('<<help_desk_bot>> get_kendra_answer() - response = ' + json.dumps(response)) 
    
    #
    # determine which is the top result from Kendra, based on the Type attribue
    #  - QUESTION_ANSWER = a result from a FAQ: just return the FAQ answer
    #  - ANSWER = text found in a document: return the text passage found in the document plus a link to the document
    #  - DOCUMENT = link(s) to document(s): check for several documents and return the links
    #
    
    first_result_type = ''
    try:
        first_result_type = response['ResultItems'][0]['Type']
    except KeyError:
        return None

    if first_result_type == 'QUESTION_ANSWER':
        try:
            faq_answer_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
        except KeyError:
            faq_answer_text = "Sorry, I could not find an answer in our FAQs."

        return faq_answer_text

    elif first_result_type == 'ANSWER':
        # return the text answer from the document, plus the URL link to the document
        try:
            document_title = response['ResultItems'][0]['DocumentTitle']['Text']
            document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
            document_url = response['ResultItems'][0]['DocumentURI']
            answer_text = "I couldn't find a specific answer, but here's an excerpt from a document ("
            answer_text += "<" + document_url + "|" + document_title + ">"
            answer_text += ") that might help:\n\n" + document_excerpt_text + "...\n"            
        except KeyError:
            answer_text = "Sorry, I could not find the answer in our documents."

        return answer_text

    elif first_result_type == 'DOCUMENT':
        # assemble the list of document links
        document_list = "Here are some documents you could review:\n"
        for item in response['ResultItems']:
            document_title = None
            document_url = None
            if item['Type'] == 'DOCUMENT':
                if item.get('DocumentTitle', None):
                    if item['DocumentTitle'].get('Text', None):
                        document_title = item['DocumentTitle']['Text']
                if item.get('DocumentId', None):
                    document_url = item['DocumentURI']
            
            if document_title is not None:
                document_list += '-  <' + document_url + '|' + document_title + '>\n'

        return document_list

    else:
        return None
