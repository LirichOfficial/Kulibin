import json
import os

#def get_user_data(user):
    #with open('stats.json') as dtb:
    #    db=json.load(dtb)
    #return db['user']


def add_new_game(user,points,date,theme,answer):
    db_games=json.load(open('games.json'))
    db_stats=json.load(open('stats.json'))

    game_value={}
    game_value['points']=points
    game_value['date']=date
    game_value['theme']=theme
    game_value['answer']=answer

    stat_value={}
    stat_value['points']=points
    stat_value['games_count']=1
    stat_value['avg']=points

    if not user in db_games:
        db_games[user]=[game_value]
    else:
        stat_value['points']+=db_stats[user]['points']
        stat_value['games_count']+=db_stats[user]['games_count']
        stat_value['avg']=stat_value['points']/stat_value['games_count']
        db_games[user].append(game_value)
    
    db_stats[user]=stat_value
    with open('stats.json','w') as file:
        json.dump(db_stats,file)
    with open('games.json','w') as file:
        json.dump(db_games,file)


def get_global_stats():
    answer=[]

def get_user_in_global_stats(user):
    pass

add_new_game('gay',52,-1,'penis','anus')
#get_global_stats()
