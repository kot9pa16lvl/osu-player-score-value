import requests
import json
from time import sleep
import time
Api_key = '' #your osu api key here
REQ_LIMIT = 59 #per  minute




all_player_range_RU = range(10, 200) #Page range of russian players for database
all_player_range_US = range(10, 200) #Page range of us players for database
target_country = "RU" #calculate score numbers for country 
player_range = range(15, 72) #pages of wanted country
all_player_range_KR = range(6, 31)
#all_player_range_RU = range(15, 16)
#all_player_range_US = range(15, 16)
#player_range = range(15, 16)


def get_players_from_page(page, country):
    url  = "https://osu.ppy.sh/rankings/osu/performance?country=" + country + "&page=" + str(page) +  "#scores"
    res = requests.get(url) 
    spl =  res.text.split('\n')
    nicknames = []
    for i in range(len(spl)):
        elem = spl[i]
        if "data-user-id" in elem:
            nicknames.append(spl[i + 3][32:])
    #print(res.text)
    return nicknames


def get_score_identity(country):
    all_player_range = range(15, 16)
    if (country ==  "RU"):
        all_player_range = all_player_range_RU
    if (country ==  "US"):
        all_player_range = all_player_range_US
    if (country == "KR"):
        all_player_range = all_player_range_KR
    scores_cnt_dict = dict()

    for page in all_player_range:
        nicknames =  get_players_from_page(page, country)
        
        for user in nicknames:
            start_time = time.time()
            scores_limit = 100
            url = 'https://osu.ppy.sh/api/get_user_best?u=' + user +  "&k=" + Api_key + "&limit=" + str(scores_limit)
            res = requests.get(url)
            
            scores = json.loads(res.text)
            for score in scores:
                beatmap_id = score['beatmap_id']
                mods = score['enabled_mods']
                score_tuple = tuple([beatmap_id, mods])
                if score_tuple in scores_cnt_dict:
                    scores_cnt_dict[score_tuple] += 1
                else:
                    scores_cnt_dict[score_tuple] = 1
                end_time = time.time()
            sleep_time = 1 / REQ_LIMIT * 60 - (end_time - start_time)
            sleep(max(0, sleep_time))
            end_time = time.time()
            print("user ", user, ", finished with ", end_time - start_time,  " seconds.", sep = "")
    return scores_cnt_dict
            

def get_dict(country):
    if country == "RU":
        f = open("ruScores.txt",  'r')
    elif  country  ==  "US":
        f = open("usScores.txt", 'r')
    ruD = f.readline().rstrip()
    ruD = ruD.split(',')
    
    dc  = dict()
    for i in range(0,  len(ruD), 2):
        s = []
        for  elem in ruD[i]:
            if elem in '0123456789':
                s.append(elem)
        bid = int(''.join(s))
        s = []
        ss = ruD[i + 1].split(':')
        for  elem  in ss[0]:
            if  elem  in  '0123456789':
                s.append(elem)
        mods = int(''.join(s))
        s = []
        for  elem in ss[1]:
            if elem in '0123456789':
                s.append(elem)
        cnt = int(''.join(s))
        dc[tuple([bid,  mods])] = cnt
    f.close()
    return dc

ruD  =  dict()
usD  =  dict()
def  get_dict2(country):
    if country == "RU":
        return ruD
    if  country == "US":
        return  usD
def get_talents_info():
    ruD = get_dict("RU")
    usD = get_dict("US")

    talents_info = dict()
    for page in player_range:
        nicknames =  get_players_from_page(page,  target_country)
        for user in nicknames:
            talents_info[user] = []
            start_time = time.time()
            scores_limit = 100
            url = 'https://osu.ppy.sh/api/get_user_best?u=' + user +  "&k=" + Api_key + "&limit=" + str(scores_limit)
            res = requests.get(url)
            
            scores = json.loads(res.text)
            for score in scores:
                beatmap_id = int(score['beatmap_id'])
                mods = int(score['enabled_mods'])
                pp = score["pp"]
                unq = 0
                cur_tuple =  tuple([beatmap_id,  mods])
                
                if  cur_tuple in ruD:
                    unq += ruD[cur_tuple]
                if  cur_tuple in usD:
                    unq += usD[cur_tuple]
                #print(cur_tuple,unq)
                talents_info[user].append([beatmap_id, mods,  pp,  unq])
            end_time = time.time()
            sleep_time = 1 / REQ_LIMIT * 60 - (end_time - start_time)
            sleep(max(0, sleep_time))
            end_time = time.time()
            print("user ", user, ", finished with ", end_time - start_time,  " seconds.", sep = "")
    return talents_info


def  get_mods(modnum):
    mods  =  ['NF', 'EZ', "", "HD", 'HR', "SD",  "DT", "RX",  "HT",  "", "FL", "AU",  "SO",  "AP"]

    curmods = []
    for i in range(len(mods)):
        if  (modnum % 2 == 1):
            curmods.append(mods[i])
        modnum //= 2
    return curmods
        
def get_talents():
    f = open("talents_info2.txt",  "r")
    n  =  int(f.readline().rstrip())
    
    talents_perfomance = []
    
    for i  in  range(n):
        user =  f.readline().rstrip()

       # print(user)
        scores_cnt  =  int(f.readline().rstrip())
        score_values  = []
        for j  in  range(scores_cnt):
            score  = list(f.readline().split())  #id,  mods,  pp,  unq
            score_values.append([100 * 0.99  **  (int(score[3])**(5/4)), score[0],  score[2],  score[1]])
        score_values.sort(reverse=True)
        player_perfomance =  0
        for i in  range(len(score_values)):
            player_perfomance += score_values[i][0] *  0.95 ** i
        talents_perfomance.append([player_perfomance, user, score_values])

    talents_perfomance.sort(reverse=True)
    f = open("dragon results.txt", "w")
    for i  in range(2, len(talents_perfomance)):
        #print(talents_perfomance[i][1])
        print("No", i - 1,  "-", talents_perfomance[i][1], talents_perfomance[i][0], file=f)
        for elem in talents_perfomance[i][2]:
            
            print("  ", "map id: ", elem[1], ", pp: ", elem[2], ", mods: ",  ''.join(get_mods(int(elem[3]))), ",  Uniqueness: ",  elem[0], sep='', file=f)
        print(file=f)

ruD  =  get_score_identity("RU")
fru  = open("ruScores.txt","w")
print(str(ruD), file = fru)
fru.close()
usD  =  get_score_identity("US")
fus = open("usScores.txt",  "w")
print(str(usD),  file = fus)
fus.close()

talents_info =  get_talents_info()
f = open('talents_info2.txt',  'w')
print(len(talents_info), file = f)
for user in talents_info:
    print(user, file = f)
    print(len(talents_info[user]), file=f)
    for info in talents_info[user]:
        print(info[0], info[1], info[2], info[3], file=f)
f.close()
get_talents()
'''
ruD  = get_dict("RU")
usD =  get_dict("US")

for beatmap  in  usD:
    if beatmap in ruD:
        ruD[beatmap]  +=  usD[beatmap]
    else:
        ruD[beatmap]  = usD[beatmap]
a = []
for beatmap  in ruD:
    a.append([ruD[beatmap], beatmap])
a.sort()
'''
