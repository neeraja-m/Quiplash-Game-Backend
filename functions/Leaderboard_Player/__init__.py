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
    logging.info(req.get_json())

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)


    top_num = req.get_json().get('top')


    players_list = list(players_container.query_items(
                                    query='SELECT TOP @num p.id, p.games_played, p.total_score FROM p ORDER BY p.total_score DESC',
                                    parameters=[
                               {'name':'@num',  'value': top_num}
                            ],
                                    enable_cross_partition_query=True
                                ))

    for i in players_list:

        i['username']= i['id']
        i['score'] = i['total_score']
        del i['id']
        del i['total_score']
        logging.info(i)
        
    logging.info("================sorted1==============")
    temp_list = sorted(players_list, key=lambda d: d['username'], reverse=False) 

    for i in temp_list:
        logging.info(i)
    logging.info("================sorted2==============")

    final_list = sorted(temp_list, key=lambda d: d['score'], reverse=True) 

    for i in final_list:
        logging.info(i)


    return func.HttpResponse(json.dumps(final_list))


  
    


