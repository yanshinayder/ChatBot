import json
import os

from helpers import kendra_client
from lambda_function import logger


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
    # determine which is the top result from Amazon Kendra, based on the Type attribute
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