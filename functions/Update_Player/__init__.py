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


    username = req.get_json().get('username')
    logging.info('========username===========: '+ username)
    password = req.get_json().get('password')
    logging.info('========password===========: '+ password)

    add_to_games_played = req.get_json().get('add_to_games_played')
    add_to_score = req.get_json().get('add_to_score')

    add_to_games_req = False
    add_to_score_req = False


    if not add_to_games_played:
        add_to_games_req = False
        add_to_games_played=0
    else:
        add_to_games_req = True
        add_to_games_played = int(add_to_games_played)

    if not add_to_score:
        add_to_score_req = False
        add_to_score=0
    else:
        add_to_score_req = True
        add_to_score = int(add_to_score)

    # pc =0

    # check if username and password match if username exists
    
    username_exists=False
    details_match=False


    try:
        logging.info(username)

        player = players_container.read_item(item=username, partition_key=username)
        username_exists =True
    except:
        logging.info('user not found')
        username_exists = False


    # players_match = players_container.query_items(
    #         query = """SELECT * FROM p
    #             WHERE p.id = @username
    #             """,
    #         parameters=[{"name" : "@username" , "value" : username}],
    #         enable_cross_partition_query=True      
    #     )

    # for player in players_match:
    #     pc=pc+1
    #     logging.info('========user found: =========== ' + str(player.get('id')))

    # logging.info(pc)

    # check if user exists
    if username_exists:
        actual_password = player.get('password')
        logging.info('========actual password: ===========' + str(actual_password))
    else:
        username_exists=False
        logging.info('========user not found===========')
        return func.HttpResponse(json.dumps({"result": False , "msg": "user does not exist"}))



    # check if details match
    if (username_exists and actual_password == password):
        details_match =True
        logging.info('========details match===========')
    else :
        logging.info('========details do not match===========')
        logging.info(password)
        return func.HttpResponse(json.dumps({"result": False , "msg": "wrong password"}))



    # check if any negative values
    if (add_to_games_req and add_to_games_played <= 0) or (add_to_score_req  and add_to_score <= 0):
        logging.info('========invalid values===========')
        return func.HttpResponse(json.dumps({"result": False , "msg": "Value to add is <=0"}))

    else: 
        try:
            logging.info('========updating values===========')
            player['games_played'] =  (player.get('games_played') + add_to_games_played)
            player['total_score'] = (player.get('total_score') + add_to_score)
            players_container.upsert_item(player)
            return func.HttpResponse(json.dumps({"result": True , "msg": "OK"}))

        except:
            return func.HttpResponse(json.dumps({"result": False , "msg": "wrong password"}))

    


