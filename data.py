import json
import os

def get_user_data(user):
    with open('stats.json') as dtb:
        db=json.load(dtb)
    return db['user']


def add_new_game(user,points,date,theme,answer):
    with open('games.json') as dtb:
        db_games=json.load(dtb)
    with open('stats.json') as dtb:
        db_stats=json.load(dtb)

    value={}
    value['points']=points
    value['date']=date
    value['theme']=theme
    value['answer']=answer

    db_games[user].append(value)
    db_stats[user]['points']+=points
    db_stats[user]['games_count']+=1
    db_stats[user]['avg']=db_stats[user]['points']/db_stats[user]['games_count']


def get_global_stats():
    pass
def get_user_in_global_stats(user):
    pass
