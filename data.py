import json
import os

def pre_add(user):
    db_games=json.load(open('games.json'))
    db_stats=json.load(open('stats.json'))
    if user in db_games:
        return

    stat_value={}
    stat_value['points']=0
    stat_value['games_count']=0

    db_games[user]=[]
    db_stats[user]=stat_value
    with open('stats.json','w') as file:
        json.dump(db_stats,file)
    with open('games.json','w') as file:
        json.dump(db_games,file)
    update_backups()

def get_user_data(user):
    pre_add(user)
    db_stats=json.load(open('stats.json'))
    return db_stats[user]

def init():
    db_games_backup=json.load(open('games_backup.json'))
    db_stats_backup=json.load(open('stats_backup.json'))
    with open('games.json','w') as file:
        json.dump(db_games_backup,file)
    with open('stats.json','w') as file:
        json.dump(db_stats_backup,file)

def update_backups():
    db_games=json.load(open('games.json'))
    db_stats=json.load(open('stats.json'))
    with open('games_backup.json','w') as file:
        json.dump(db_games,file)
    with open('stats_backup.json','w') as file:
        json.dump(db_stats,file)


def add_new_game(user,points,date,theme,answer):
    pre_add(user)
    db_games=json.load(open('games.json'))
    db_stats=json.load(open('stats.json'))

    game_value={}
    game_value['points']=points
    game_value['date']=date
    game_value['theme']=theme
    game_value['answer']=answer

    stat_value={}
    stat_value['points']=points+db_stats[user]['points']
    stat_value['games_count']=db_stats[user]['games_count']+1



    db_games[user].append(game_value)
    db_stats[user]=stat_value
    with open('stats.json','w') as file:
        json.dump(db_stats,file)
    with open('games.json','w') as file:
        json.dump(db_games,file)
    update_backups()


def get_global_stats():
    db_stats=json.load(open('stats.json'))
    users=list(db_stats.keys())

    users_value=[]
    for user in users:
        cur_points=db_stats[user]['points']
        users_value.append([cur_points,user])
    users_value.sort(reverse=True)

    while len(users_value)>10:
        users_value.pop()
    
    answer=[]
    for points,user in users_value:
        current={}
        current['points']=points
        current['user']=user
        answer.append(current)
    return answer

def get_user_place(global_user):
    pre_add(global_user)
    db_stats=json.load(open('stats.json'))
    users=list(db_stats.keys())

    users_value=[]
    for user in users:
        cur_points=db_stats[user]['points']
        users_value.append([cur_points,user])
    users_value.sort(reverse=True)

    answer=[]

    for i in range(len(users_value)):
        if users_value[i][1]!=global_user:
            continue
        l=max(0,i-2)
        r=min(len(users_value),i+3)
        for j in range(l,r):
            answer.append(users_value[j])
            answer[-1].append(j)

    final=[]
    for points,user,pos in answer:
        current={}
        current['points']=points
        current['user']=user
        current['position']=pos
        final.append(current)
    return final
