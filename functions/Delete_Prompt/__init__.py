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

    id = req.get_json().get('id')
    username = req.get_json().get('username')
    password = req.get_json().get('password')

     # check if username and password match if username exists
    
    id_exists=False
    details_match=False
    username_exists = False

    try:
        logging.info(username)
        player_username = players_container.read_item(item=username, partition_key=username)
        username_exists =True
    except:
        logging.info('user not found')
        username_exists = False


    try:
        logging.info(id)
        player_id = prompts_container.read_item(item=str(id), partition_key=str(id))
        id_exists =True
    except:
        logging.info('user id not found')
        id_exists = False



    # check if user exists
    if username_exists:
        actual_password = player_username.get('password')
        logging.info('========actual password: ===========' + str(actual_password))
    else:
        username_exists=False
        logging.info('========user not found===========')
        return func.HttpResponse(json.dumps({"result": False, "msg": "bad username or password"}))


    # check if id exists
    if id_exists ==False:
        logging.info('========user id not found===========')
        return func.HttpResponse(json.dumps({"result": False, "msg": "prompt id does not exist"}))

        
    if (username_exists and actual_password == password):
        details_match =True
        logging.info('========details match===========')
        prompt_list = list(prompts_container.query_items(
                        query='SELECT * FROM p WHERE p.username=@username AND p.id=@id',
                        parameters=[
                            {'name':'@username',  'value':username},
                            {'name':'@id',  'value':str(id)}
                        ],
                        enable_cross_partition_query=True
                    ))


        if(len(prompt_list)>0):
                logging.info("prompt exists for this user:")
                logging.info('========deleting prompt ========')
                
                for prompt in prompt_list:
                    prompts_container.delete_item(item=prompt['id'], partition_key=prompt['id'])
                return func.HttpResponse(json.dumps({"result": True , "msg": "OK"}))

        else:

                logging.info('======== id does not match username =========')
                
                return func.HttpResponse(json.dumps({"result": False, "msg": "access denied"}))


    else:
        logging.info('========details do not match===========')
        return func.HttpResponse(json.dumps({"result": False, "msg": "bad username or password"}))

   



            
            