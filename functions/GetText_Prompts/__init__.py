import logging

import azure.functions as func
import json
import os
import azure.cosmos as cosmos
import random
import uuid
import re


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

    word = req.get_json().get('word')
    exact = req.get_json().get('exact')
    

    all_prompt_list = list(prompts_container.query_items(
                                    query='SELECT p.id,p.text,p.username FROM p',
                                    parameters=[
                                
                            ],
                                    enable_cross_partition_query=True
                                ))
    prompts_to_return =[]
    for i in all_prompt_list:
        logging.info(i)
        temp = re.split('[?.,'' !:;]', str(i))
        del temp[:6] 
        del temp[-5:] 
        logging.info(temp)
        if(exact==False):
            if(str(word).upper() in map(str.upper,temp)):
                logging.info("word found")
                prompts_to_return.append(i)
        else:
            if(str(word) in temp):
                logging.info("word found")
                prompts_to_return.append(i)

    for j in prompts_to_return:
        logging.info("====== all prompts ======")
        logging.info(j)
    
    return func.HttpResponse(json.dumps(prompts_to_return))




        




        
    return func.HttpResponse(json.dumps([]))


