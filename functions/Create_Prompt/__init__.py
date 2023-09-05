import logging

import azure.functions as func
import json
import os
import azure.cosmos as cosmos
import random
import uuid

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

    logging.info(req.get_json())
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)
    prompts_container = db_client.get_container_client(prompts_cont)

    text = req.get_json().get('text')
    username = req.get_json().get('username')
    password = req.get_json().get('password')

     # check if username and password match if username exists
    username_exists=False
    details_match=False

    pc=0

    prompt_exists = False

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
        return func.HttpResponse(json.dumps({"result": False , "msg": "bad username or password"}))

        
    if (username_exists and actual_password == password):
        details_match =True
        logging.info('========details match===========')
    else:
        logging.info('========details do not match===========')
        return func.HttpResponse(json.dumps({"result": False , "msg": "bad username or password"}))

    if(len(text)> 100 or len(text) <20):
        logging.info('========invalid prompt length===========')
        return func.HttpResponse(json.dumps({"result": False , "msg": "prompt length is <20 or > 100 characters"}))

    prompt_list = list(prompts_container.query_items(
                query='SELECT * FROM p WHERE p.username=@username AND p.text=@text',
                parameters=[
                    {'name':'@username',  'value':username},
                    {'name':'@text',  'value':text}
                ],
                enable_cross_partition_query=True
            ))

    if(len(prompt_list)>0):
        logging.info("prompt already exists for this user:")

        prompt_exists=True
        return func.HttpResponse(json.dumps({
                "result": False, "msg": "This user already has a prompt with the same text"}))

    else:

            idd=random.randint(0, 100000000000)
            prompt = {'id': str(idd), 'username': username,'text': text}
            # logging.info(prompt)
            prompts_container.create_item(prompt)
            logging.info("prompt successfully added:")
            return func.HttpResponse(json.dumps({
                "result" : True, "msg": "OK"}))
    

            
            