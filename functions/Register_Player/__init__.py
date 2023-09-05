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



    if (len(username)<4 or len(username)>16):
        logging.info("================username invalid=================")

        return func.HttpResponse(json.dumps({"result": False ,"msg" : "Username less than 4 characters or more than 16 characters"}))
        #check if password is within character limit
    if(len(password)>24 or len(password)<8):
        logging.info("================password invalid=================")

        return func.HttpResponse(json.dumps({"result": False ,"msg" : "Password less than 8 characters or more than 24 characters"}))
    
    else:
        try:
            logging.info("================player successfully registered=================")
            player = {'id': username, 'password': password,'games_played': 0, 'total_score':0}
            players_container.create_item(player)

            # player={}
            # player['id'] = username
            # player['password'] = password
            # player['total_score'] = 0
            # player['games_played'] = 0
            # del  player['username']
                        
            return func.HttpResponse(json.dumps({
             "result" : True, "msg": "OK"}))
        except:
            logging.info("================player already registered=================")
            return func.HttpResponse(json.dumps({"result": False ,"msg" : "Username already exists"}))


