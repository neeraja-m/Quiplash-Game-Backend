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

    num_to_get = req.get_json().get('prompts')
    players_list = req.get_json().get('players')
    
    if(num_to_get):
        logging.info("getting "+ str(num_to_get) + " prompts")

        prompt_list = list(prompts_container.query_items(
                    query='SELECT * FROM p',
                    enable_cross_partition_query=True
                ))

        for prompt in prompt_list:
            del prompt['_attachments']
            del prompt['_etag']
            del prompt['_rid']
            del prompt['_self']
            del prompt['_ts']
            logging.info(prompt)


        if(len(prompt_list)<=num_to_get):
            logging.info("returning all prompts")
            return func.HttpResponse(json.dumps(prompt_list))

        else:
            logging.info("returning " + str(num_to_get)+ " random prompts")

            to_output = random.sample(prompt_list,num_to_get) 
            logging.info(to_output)

        return func.HttpResponse(json.dumps(to_output))

    else: 

        logging.info("getting all prompts from players")
        plist=[]
        for pl in players_list:

            prompt_list = list(prompts_container.query_items(
                                    query='SELECT p.id, p.text, p.username FROM p WHERE p.username = @username',
                                    parameters=[
                                {'name':'@username',  'value': pl},
                            ],
                                    enable_cross_partition_query=True
                                ))
            plist.append(prompt_list)
    
        final_list = []
        for sublist in plist:
            for item in sublist:
                final_list.append(item)

        for j in final_list:
            logging.info(j)
                
        return func.HttpResponse(json.dumps(final_list))
       
    




            
            