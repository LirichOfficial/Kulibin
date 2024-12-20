import json
import os
import matplotlib.pyplot as plt

enc='utf-8'
def pre_add(user):
    db_games=json.load(open('games.json',encoding=enc))
    db_stats=json.load(open('stats.json',encoding=enc))
    if user in db_games:
        return

    stat_value={}
    stat_value['points']=0
    stat_value['games_count']=0

    db_games[user]=[]
    db_stats[user]=stat_value
    with open('stats.json','w',encoding=enc) as file:
        json.dump(db_stats,file,ensure_ascii=False,indent=4)
    with open('games.json','w',encoding=enc) as file:
        json.dump(db_games,file,ensure_ascii=False,indent=4)
    update_backups()

def get_user_data(user):
    pre_add(user)
    db_stats=json.load(open('stats.json'))
    return db_stats[user]

def init():
    db_games_backup=json.load(open('games_backup.json',encoding=enc))
    db_stats_backup=json.load(open('stats_backup.json',encoding=enc))
    with open('games.json','w',encoding=enc) as file:
        json.dump(db_games_backup,file,ensure_ascii=False,indent=4)
    with open('stats.json','w',encoding=enc) as file:
        json.dump(db_stats_backup,file,ensure_ascii=False,indent=4)

def update_backups():
    db_games=json.load(open('games.json',encoding=enc))
    db_stats=json.load(open('stats.json',encoding=enc))
    with open('games_backup.json','w',encoding=enc) as file:
        json.dump(db_games,file,ensure_ascii=False,indent=4)
    with open('stats_backup.json','w',encoding=enc) as file:
        json.dump(db_stats,file,ensure_ascii=False,indent=4)


def add_new_game(user,points,date,theme,answer):
    pre_add(user)
    db_games=json.load(open('games.json',encoding=enc))
    db_stats=json.load(open('stats.json',encoding=enc))

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
    with open('stats.json','w',encoding=enc) as file:
        json.dump(db_stats,file,ensure_ascii=False,indent=4)
    with open('games.json','w',encoding=enc) as file:
        json.dump(db_games,file,ensure_ascii=False,indent=4)
    update_backups()


def get_global_stats():
    db_stats=json.load(open('stats.json',encoding=enc))
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
    db_stats=json.load(open('stats.json',encoding=enc))
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

def get_plot_image(user):
    pre_add(user)
    db_games=json.load(open('games.json',encoding=enc))
    games=db_games[user]

    x=[0]
    y=[0]
    cur_points=0
    minv=0
    maxv=0
    for i in range(len(games)):
        game=games[i]
        x.append(i+1)
        cur_points+=game['points']
        y.append(cur_points)
        minv=min(minv,cur_points)
        maxv=max(maxv,cur_points)

    minv-=100
    maxv+=100
    plt.axis([0,len(games)+2,minv,maxv])
    plt.title('статистика игрока '+user)
    plt.plot(x, y,'m-o')
    plt.savefig('Plot.png')

init()
get_plot_image('AZakirow')