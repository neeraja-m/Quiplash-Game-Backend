import logging

import azure.functions as func
import json
import os
import azure.cosmos as cosmos

# db_URI = os.environ['db_URI']
# db_id = os.environ['db_id']
# db_key = os.environ['db_key']
# players_cont = os.environ['players_container']
# prompts_cont = os.environ['prompts_container']

import config
db_URI = config.settings['db_URI']
db_id = config.settings['db_id']
db_key = config.settings['db_key']
players_cont = config.settings['players_container']
prompts_cont = config.settings['prompts_container']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('=====Python HTTP trigger function processed a request=====')
    
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    username = req.get_json().get('username')
    logging.info('========username===========: '+ username)
    password = req.get_json().get('password')
    logging.info('========password===========: '+ password)


    # check if username and password match if username exists
    username_exists=False
    details_match=False

    pc=0

    players_match = players_container.query_items(
            query = """SELECT * FROM p
                WHERE p.id = @username
                """,
            parameters=[{"name" : "@username" , "value" : username}],
            enable_cross_partition_query=True      
        )
    
    for player in players_match:
        pc=pc+1
        
        logging.info('========user found: =========== ' + str(player.get('id')))

    if pc==1:
        username_exists=True
        actual_password = player.get('password')
        logging.info('========actual password: ===========' + str(actual_password))

    else:
        logging.info('========user not found===========')

        
    if (username_exists and actual_password == password):
        details_match =True
        logging.info('========details match===========')
    else:
        logging.info('========details do not match===========')

    try:

            if details_match:

                return func.HttpResponse(json.dumps({
             "result" : True, "msg": "OK"}))
            else:
                return func.HttpResponse(json.dumps({"result": False , "msg": "Username or password incorrect"}))
    except:

            logging.info("================username or password incorrect=================")

    return func.HttpResponse(json.dumps({"result": False , "msg": "Username or password incorrect"}))


