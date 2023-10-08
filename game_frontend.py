import requests,json
from time import sleep
from loguru import logger

om_frontend = 'http://34.142.198.17:51504/v1/frontendservice/tickets'

def create_ticket(body):
    resp = requests.post(om_frontend, data=json.dumps(body))
    return resp.text

def get_ticket_assignments(ticket_id):
    resp = requests.get(om_frontend + '/' + ticket_id)
    return resp.text


body = {
  "ticket": {
    "search_fields": {
        "double_args": {
            "level": 35
        },
        "string_args":{
            "role": "tank"
        },
        "tags":["wow"]
    }
  }
}

# resp = json.loads(create_ticket(body))
# ticket_id = resp['id']
# logger.info("ticket_id: %s" % ticket_id)

# resp = get_ticket_assignments(ticket_id)
# logger.info(resp)
# print('done')