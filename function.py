from flask import Flask, request, abort
import json, sys
import requests
from loguru import logger
import uuid

app = Flask(__name__)

logger.remove()
logger.add(sys.stdout, level='DEBUG')

query_tickets_svc = "http://34.143.251.204:51503/v1/queryservice/tickets:query"
query_backfills_svc = "http://34.143.251.204:51503/v1/queryservice/backfills:query"

def query_tickets_pool(parameters):
    result = {}
    resp = requests.post(query_tickets_svc, json=parameters)
    if resp.text != '':
        result = json.loads(resp.text)
    return result


def query_backfills_pool(parameters):
    result = {}
    resp = requests.post(query_backfills_svc, json=parameters)
    if resp.text != '':
        result = json.loads(resp.text)
    return result


def fullmatch(tickets):
    result = ''
    while len(tickets) >= 2:
        logger.debug(len(tickets))
        match_id = uuid.uuid4().hex
        match_function = "fullmatch"
        result += json.dumps({
            "result":{
                "proposal":{
                    "match_id": match_id, 
                    "match_profile": "string", 
                    "match_function": match_function, 
                    "tickets": tickets[0:2],
                    "allocate_gameserver": True
                    }
                }
            })
        del tickets[0:2]
    logger.debug("Match: " + result)
    return result


def match_new_backfill(tickets):
    match_id = uuid.uuid4().hex
    match_function = "match_new_backfill"
    backfill = {
            "search_fields": {
                "double_args": {
                    "level": 47
                },
                "tags":["wow"]
            },

        }
    result = json.dumps({
        "result":{
            "proposal":{
                "match_id": match_id, 
                "match_profile": "string", 
                "match_function": match_function, 
                "tickets": tickets, 
                "backfill": backfill,
                "allocate_gameserver": True
                }
            }
        })
    logger.debug("Match: " + result)
    return result


def match_with_backfill(tickets, backfills):
    match_id = uuid.uuid4().hex
    match_function = "match_with_backfill"
    result = json.dumps({
        "result":{
            "proposal":{
                "match_id": match_id, 
                "match_profile": "string", 
                "match_function": match_function, 
                "tickets": tickets, 
                "backfill": backfills[0],
                "allocate_gameserver": False
                }
            }
        })
    logger.debug("Match: " + result)
    return result


@app.route('/v1/matchfunction:run',methods = ['POST'])
def index():
    match_result = ''
    data = request.json
    # logger.debug("profile_name: %s" % data['profile']['name'])
    logger.debug("request data: %s" % json.dumps(data))
    for pool in data['profile']['pools']:
        backfills = []
        tickets = []
        parameters = {"pool":pool}
        tickets_result = query_tickets_pool(parameters)
        backfills_result = query_backfills_pool(parameters)
        if tickets_result.get('result'):
            tickets = tickets_result['result']['tickets']
        if backfills_result.get('result'):
            backfills = backfills_result['result']['backfills']
        logger.debug("pool name: %s, tickets num: %d, backfill num: %d" %(pool['name'], len(tickets),len(backfills)) )

        # tickets数量大于2, 直接对tickets进行匹配
        if len(tickets) >= 2:
            match_result += fullmatch(tickets)

        # tickets数量不足并且没有backfill的情况
        if len(tickets) == 1 and len(backfills) == 0:
            match_result += match_new_backfill(tickets)

        # 有backfill存在, 优先匹配backfill
        if len(tickets) > 0 and len(backfills) > 0:
            match_result += match_with_backfill(tickets, backfills)
    return match_result


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')


# def create_backfill():
#     body = {
#         "backfill": {
#             "search_fields": {
#                 "double_args": {
#                     "level": 35
#                 },
#                 "tags":["wow"]
#             }
#         }
#     }
#     resp = requests.post('http://34.124.155.15:51504/v1/frontendservice/backfills', data=json.dumps(body))
#     return resp.text
    # backfill = json.loads(create_backfill())    