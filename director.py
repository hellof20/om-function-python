import requests,json,sys
from loguru import logger

logger.remove()
logger.add(sys.stdout, level='DEBUG')

om_match_function_host = "35.202.71.205"
om_match_function_port = 8080
om_backend = "http://34.126.178.134:51505/v1/backendservice/"
om_frontend = "http://34.124.155.15:51504/v1/frontendservice/"

def matches_fetch(body):
    resp = requests.post(om_backend + 'matches:fetch', data=json.dumps(body))
    return resp.text

def tickets_assign(body):
    resp = requests.post(om_backend + 'tickets:assign', data=json.dumps(body))
    return resp.text

def get_ticket(ticket_id):
    resp = requests.get(om_frontend + 'tickets/'+ticket_id)
    return resp.text

def acknowledge_backfill(backfill_id, body):
    resp = requests.post(om_frontend + 'backfills/'+backfill_id+'/acknowledge', data=json.dumps(body))
    return resp.text

match_body = {
    "config":{
        "host": om_match_function_host,
        "port": om_match_function_port,
        "type": "REST"
    },
    "profile":{
        "name": "profile1",
        "pools":[
            {
                "name": "low_level_pool",
                "double_range_filters": [
                    {
                        "double_arg": "level",
                        "max": 50,
                        "min": 0
                    }
                ],
                "tag_present_filters": [{"tag": "wow"}]
            },
            {
                "name": "high_level_pool",
                "double_range_filters": [
                    {
                        "double_arg": "level",
                        "max": 100,
                        "min": 51
                    }
                ],
                "tag_present_filters": [{"tag": "wow"}]
            }
        ]
    }
}

result = {}
resp = matches_fetch(match_body)
resp_list = resp.split('\n')
resp_list.pop()
if len(resp_list) > 0:
    for resp in resp_list:
        resp_dict = json.loads(resp)
        logger.debug(resp_dict)
        if resp_dict['result']['match'].get('backfill'):
            backfill_id = resp_dict['result']['match']['backfill']['id']
            acknowledge_boy = {
                "assignment": {
                    "connection": "192.168.10.10:3000"
                    }
            }           
            result = acknowledge_backfill(backfill_id, acknowledge_boy)
            logger.debug(result)
        else:
            tickets = resp_dict['result']['match']['tickets']
            ticket_ids = []
            for ticket in tickets:
                ticket_ids.append(ticket['id'])
            ticket_assign_boy = {
                "assignments": [
                    {
                        "ticket_ids": ticket_ids,
                        "assignment": {
                            "connection": "192.168.0.1:2222"
                        }
                    }
                ]
            }
            tickets_assign(ticket_assign_boy)
            for ticket_id in ticket_ids:
                result = get_ticket(ticket_id)
                logger.debug(result)
        
else:
    logger.debug('current no match')