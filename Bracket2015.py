import pandas as pd
import requests
from bs4 import BeautifulSoup

#function to loop through and collect offensive and defensive scoring stats
offense = []
defense = []
def team_offense_function():
  

    for i in range(1,6):
        base_offense_url = "http://www.ncaa.com/stats/basketball-men/d1/current/team/145/p"
        #print base_offense_url+str(i)
        offense_request = requests.get(base_offense_url+str(i))
        #print offense_request
        offense_soup = BeautifulSoup(offense_request.text)
        offense_soup_text = offense_soup.tbody.get_text(",")
        offense_soup_text = str(offense_soup_text)
        offense_soup_text = offense_soup_text.split("\n")
        

        for row in offense_soup_text:
            offense.append(row)
        
        base_defense_url = "http://www.ncaa.com/stats/basketball-men/d1/current/team/146/p"
        defense_request = requests.get(base_defense_url+str(i))
        defense_soup = BeautifulSoup(defense_request.text)
        defense_soup_text = defense_soup.tbody.get_text(",")
        defense_soup_text = str(defense_soup_text)
        defense_soup_text = defense_soup_text.split("\n")
        
        for row in defense_soup_text:
            defense.append([row])
team_offense_function()

#using pandas to data munge offense stats

team_offense_df = pd.DataFrame(offense,columns=["generic"])
lista_offense = [item.split(',') for item in team_offense_df["generic"]]
lista_offense_df = pd.DataFrame(lista_offense,columns=["a","rank_off","Team","GamesPlayed","PointsFor","AvePPG","g","h"])
lista_offense_df = lista_offense_df.drop(lista_offense_df.columns[[0, 6, 7]], axis=1) 
lista_offense_df = lista_offense_df.drop(lista_offense_df.columns[[2, 3]], axis=1) 
lista_offense_df = lista_offense_df.fillna(lista_offense_df.mean())

#using pandas to data munge defense stats
team_defense_df = pd.DataFrame(defense,columns=["generic"])
lista_defense = [item.split(',') for item in team_defense_df["generic"]]
lista_defense_df = pd.DataFrame(lista_defense,columns=["a","rank_def","Team","GamesPlayed","PointsAgainst","AvePPGAgainst","g","h"])
lista_defense_df = lista_defense_df.drop(lista_defense_df.columns[[0, 6, 7]], axis=1) 
lista_defense_df = lista_defense_df.drop(lista_defense_df.columns[[2, 3]], axis=1)

lista_defense_df.fillna(0, inplace=True)

#merging offense and defense stats together, into the offense table and handling null values
full_lista_offense=pd.DataFrame(lista_offense_df.merge(lista_defense_df, on='Team', how='outer')).dropna(how="all")
full_lista_offense["AvePPGAgainst"]=full_lista_offense["AvePPGAgainst"].fillna(value=60.9)
full_lista_offense["AvePPG"]=full_lista_offense["AvePPG"].fillna(value=73.2)

#bringing in RPI as another metric, from another source Fixing Kentucky Row due to excess columns
SOS = requests.get("http://warrennolan.com/basketball/2015/rpi")
SOS_soup = BeautifulSoup(SOS.text)
SOS_soup_tbody = SOS_soup.tbody.get_text()
SOS_soup_tbody = str(SOS_soup_tbody.strip(" "))
SOS_soup_tbody = SOS_soup_tbody.replace("\n",",").split(",,")


SOS_list = []
for row in SOS_soup_tbody:
    SOS_list.append([row])
SOS_list[1] = [',Kentucky,34,0,1.0000,1,.6780,1,.5707,25,1,1']

SOS_df = pd.DataFrame(SOS_list,columns=["generic"])

SOS_new_list = [item.split(',') for item in SOS_df["generic"]]
lista_SOS_df = pd.DataFrame(SOS_new_list,columns=["blank1","Team","W","L","WinPCt","WinRank","RPI","RPIRank","SOS","SOSRank","AP","Coaches"])

lista_SOS_df = lista_SOS_df.drop(lista_SOS_df.columns[[0,2,3,5,7,10,11]], axis=1) 

"""Bracket Selections"""

#Setting up each Region's Bracket
Midwest = ["Kentucky","Hampton","Cincinnati","Purdue","West Virginia", "Buffalo","Maryland", "Valparaiso","Butler","Texas","Notre Dame",
           "Northeastern","Wichita State","Indiana","Kansas","New Mexico State"]

West = ["Wisconsin", "Coastal Caro.", "Oregon", "Oklahoma State", "Arkansas", "Wofford", "North Carolina","Harvard","Xavier","Ole Miss",
        "Baylor","Georgia State","VCU","Ohio State","Arizona","Texas Southern"]

East = ["Villanova","Lafayette","NC State","LSU", "UNI", "Wyoming","Louisville","UC Irvine","Providence","Dayton","Oklahoma","Albany",
        "Michigan State","Georgia","Virginia","Belmont"]

South = ["Duke","Robert Morris","San Diego State", "St.John's", "Utah", "Steph.F.Austin","Georgetown","Eastern Wash.","SMU","UCLA", 
         "Iowa State", "UAB", "Iowa","Davidson","Gonzaga","North Dakota St."]
         
#Midwest Bracket Selections
#Midwest Bracket Setup. Pulls data from stats dataframe, left joins to MW teams
midwest_df = pd.DataFrame(Midwest, columns=["Team"])
midwest_df = pd.DataFrame(midwest_df.merge(full_lista_offense,on='Team', how='left'))
midwest_df["AvePPGAgainst"]=midwest_df["AvePPGAgainst"].fillna(value=60.9)
midwest_df["AvePPG"]=midwest_df["AvePPG"].fillna(value=73.2)
midwest_df["RPI"]=midwest_df["RPI"].fillna(value=.5900)

midwest = [tuple(x) for x in midwest_df.values]

#Advances to Round of 32
sweet_sixteen = []
for i in range(0, len(midwest), 2):
    difference = (float(midwest[i][2])-float(midwest[i + 1][2]) )+(float(midwest[i+1][4])-float(midwest[i][4])) + (float(midwest[i][6])-float(midwest[i + 1][6]))
    
    if float(midwest[i][2])-float(midwest[i + 1][4]) +float(midwest[i+1][2])-float(midwest[i][4]) +float(midwest[i][6])-float(midwest[i + 1][6]) >0:
        sweet_sixteen.append(midwest[i])
        print midwest[i][0] + "-higher seed wins!" + str(difference)
    else:
        sweet_sixteen.append(midwest[i+1])
        print midwest[i + 1][0]+"-lower seed wins!"+ str(difference)
print sweet_sixteen

#Advances to Sweet Sixteen
elite_eight=[]
for i in range(0, len(sweet_sixteen), 2):
    difference = (float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) )+(float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4])) + (float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]))
    if float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) +float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4]) +float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]) >0:
        elite_eight.append(sweet_sixteen[i])
        print sweet_sixteen[i][0] + "-higher seed wins!" + str(difference)

    else:
        elite_eight.append(sweet_sixteen[i+1])
        print sweet_sixteen[i + 1][0]+"-lower seed wins!"+ str(difference)
print elite_eight

#Advances to Elite Eight
final_four=[]
for i in range(0, len(elite_eight), 2):
    difference = (float(elite_eight[i][2])-float(elite_eight[i + 1][2]) )+(float(elite_eight[i+1][4])-float(elite_eight[i][4])) + (float(elite_eight[i][6])-float(elite_eight[i + 1][6]))
    if float(elite_eight[i][2])-float(elite_eight[i + 1][2]) +float(elite_eight[i+1][4])-float(elite_eight[i][4]) +float(elite_eight[i][6])-float(elite_eight[i + 1][6]) >0:
        final_four.append(elite_eight[i])
        print elite_eight[i][0] + "-higher seed wins!" + str(difference)
    else:
        final_four.append(elite_eight[i+1])
        print elite_eight[i + 1][0]+"-lower seed wins!"+ str(difference)
print final_four

#Advances as Regional Winner to Final Four
Regional_winner=[]
for i in range(0, len(final_four), 2):
    difference = (float(final_four[i][2])-float(final_four[i + 1][2]) )+(float(final_four[i+1][4])-float(final_four[i][4])) + (float(final_four[i][6])-float(final_four[i + 1][6]))
    if float(final_four[i][2])-float(final_four[i + 1][2]) +float(final_four[i+1][4])-float(final_four[i][4]) +float(final_four[i][6])-float(final_four[i + 1][6]) >0:
        Regional_winner.append(final_four[i])
        print final_four[i][0] + "-higher seed wins!" + str(difference)
    else:
        Regional_winner.append(final_four[i+1])
        print final_four[i + 1][0]+"-lower seed wins!"+ str(difference)
print Regional_winner


#West Bracket Selections
#West Bracket Setup. Pulls data from stats dataframe, left joins to West teams

west_df = pd.DataFrame(West, columns=["Team"])
west_df = pd.DataFrame(west_df.merge(full_lista_offense,on='Team', how='left'))
west_df["AvePPGAgainst"]=west_df["AvePPGAgainst"].fillna(value=60.9)
west_df["AvePPG"]=west_df["AvePPG"].fillna(value=73.2)
west_df["RPI"]=west_df["RPI"].fillna(value=.5900)

west = [tuple(x) for x in west_df.values]


#Advances to Round of 32
sweet_sixteen = []
for i in range(0, len(west), 2):
    difference = (float(west[i][2])-float(west[i + 1][2]) )+(float(west[i+1][4])-float(west[i][4])) + (float(west[i][6])-float(west[i + 1][6]))
    if float(west[i][2])-float(west[i + 1][2]) +float(west[i+1][4])-float(west[i][4]) +float(west[i][6])-float(west[i + 1][6]) >0:
       sweet_sixteen.append(west[i])
        print west[i][0] + "-higher seed wins!" + str(difference)
    else:
        sweet_sixteen.append(west[i+1])
        print west[i + 1][0]+"-lower seed wins!"+ str(difference)
print sweet_sixteen

#Advances to Sweet Sixteen
elite_eight=[]
for i in range(0, len(sweet_sixteen), 2):
    difference = (float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) )+(float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4])) + (float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]))
    if float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) +float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4]) +float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]) >0:
        elite_eight.append(sweet_sixteen[i])
        print sweet_sixteen[i][0] + "-higher seed wins!" + str(difference)
    else:
        elite_eight.append(sweet_sixteen[i+1])
        print sweet_sixteen[i + 1][0]+"-lower seed wins!"+ str(difference)
print elite_eight

#Advances to Elite Eight
final_four=[]
for i in range(0, len(elite_eight), 2):
    difference = (float(elite_eight[i][2])-float(sweet_sixteen[i + 1][2]) )+(float(elite_eight[i+1][4])-float(elite_eight[i][4])) + (float(elite_eight[i][6])-float(elite_eight[i + 1][6]))
    if float(elite_eight[i][2])-float(elite_eight[i + 1][2]) +float(elite_eight[i+1][4])-float(elite_eight[i][4]) +float(elite_eight[i][6])-float(elite_eight[i + 1][6]) >0:
        final_four.append(elite_eight[i])
        print elite_eight[i][0] + "-higher seed wins!"+ str(difference)
    else:
        final_four.append(elite_eight[i+1])
        print elite_eight[i + 1][0]+"-lower seed wins!"+ str(difference)
print final_four

#Advances as Regional Winner to Final Four
for i in range(0, len(final_four), 2):
    difference = (float(final_four[i][2])-float(final_four[i + 1][2]) )+(float(final_four[i+1][4])-float(final_four[i][4])) + (float(final_four[i][6])-float(final_four[i + 1][6]))
    if float(final_four[i][2])-float(final_four[i + 1][2]) +float(final_four[i+1][4])-float(final_four[i][4]) +float(final_four[i][6])-float(final_four[i + 1][6]) >0:
        Regional_winner.append(final_four[i])
        print final_four[i][0] + "-higher seed wins!"+ str(difference)
    else:
        Regional_winner.append(final_four[i+1])
        print final_four[i + 1][0]+"-lower seed wins!"+ str(difference)
print Regional_winner

#East Bracket Selections
#East Bracket Setup. Pulls data from stats dataframe, left joins to East teams
east_df = pd.DataFrame(East, columns=["Team"])
east_df = pd.DataFrame(east_df.merge(full_lista_offense,on='Team', how='left'))
east_df["AvePPGAgainst"]=east_df["AvePPGAgainst"].fillna(value=60.9)
east_df["AvePPG"]=east_df["AvePPG"].fillna(value=73.2)
east_df["RPI"]=east_df["RPI"].fillna(value=.5900)


east = [tuple(x) for x in east_df.values]

#Advances to Round of 32. 
sweet_sixteen = []
for i in range(0, len(east), 2):
    difference = (float(east[i][2])-float(east[i + 1][2]) )+(float(east[i+1][4])-float(east[i][4])) + (float(east[i][6])-float(east[i + 1][6]))
    if float(east[i][2])-float(east[i + 1][2]) +float(east[i+1][4])-float(east[i][4]) +float(east[i][6])-float(east[i + 1][6]) >0:
        sweet_sixteen.append(east[i])
        print east[i][0] + "-higher seed wins!" + str(difference)
    else:
        sweet_sixteen.append(east[i+1])
        print east[i + 1][0]+"-lower seed wins!"+ str(difference)
print sweet_sixteen

#Advances to Sweet Sixteen
elite_eight=[]
for i in range(0, len(sweet_sixteen), 2):
    difference = (float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) )+(float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4])) + (float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]))
    if float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) +float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4]) +float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]) >0:
        elite_eight.append(sweet_sixteen[i])
        print sweet_sixteen[i][0] + "-higher seed wins!"  + str(difference)
    else:
        elite_eight.append(sweet_sixteen[i+1])
        print sweet_sixteen[i + 1][0]+"-lower seed wins!" + str(difference)
print elite_eight

#Advances to Elite Eight
final_four=[]
for i in range(0, len(elite_eight), 2):
    difference = (float(elite_eight[i][2])-float(elite_eight[i + 1][2]) )+(float(elite_eight[i+1][4])-float(elite_eight[i][4])) + (float(elite_eight[i][6])-float(elite_eight[i + 1][6]))
    if float(elite_eight[i][2])-float(elite_eight[i + 1][2]) +float(elite_eight[i+1][4])-float(elite_eight[i][4]) +float(elite_eight[i][6])-float(elite_eight[i + 1][6]) >0:
        final_four.append(elite_eight[i])
        print elite_eight[i][0] + "-higher seed wins!"+ str(difference)
    else:
        final_four.append(elite_eight[i+1])
        print elite_eight[i + 1][0]+"-lower seed wins!"+ str(difference)
print final_four

#Advancesas Regional Winner to Final Four
for i in range(0, len(final_four), 2):
    difference = (float(final_four[i][2])-float(final_four[i + 1][2]) )+(float(final_four[i+1][4])-float(final_four[i][4])) + (float(final_four[i][6])-float(final_four[i + 1][6]))
    if float(final_four[i][2])-float(final_four[i + 1][2]) +float(final_four[i+1][4])-float(final_four[i][4]) +float(final_four[i][6])-float(final_four[i + 1][6]) >0:
        Regional_winner.append(final_four[i])
        print final_four[i][0] + "-higher seed wins!"+ str(difference)
    else:
        Regional_winner.append(final_four[i+1])
        print final_four[i + 1][0]+"-lower seed wins!"+ str(difference)
print Regional_winner

#South Bracket Selections. This region is a mess.
#South Bracket Setup. Pulls data from stats dataframe, left joins to South teams
south_df = pd.DataFrame(South, columns=["Team"])
south_df = pd.DataFrame(south_df.merge(full_lista_offense,on='Team', how='left'))
south_df["AvePPGAgainst"]=south_df["AvePPGAgainst"].fillna(value=60.9)
south_df["AvePPG"]=south_df["AvePPG"].fillna(value=73.2)
south_df["RPI"]=south_df["RPI"].fillna(value=.5900)

south = [tuple(x) for x in south_df.values]

#Advances to Round of 32. 
sweet_sixteen = []
for i in range(0, len(south), 2):
    difference = (float(south[i][2])-float(south[i + 1][2]) )+(float(south[i+1][4])-float(south[i][4])) + (float(south[i][6])-float(south[i + 1][6]))
    if float(south[i][2])-float(south[i + 1][2]) +float(south[i+1][4])-float(south[i][4]) +float(south[i][6])-float(south[i + 1][6]) >0:
        sweet_sixteen.append(south[i])
        print south[i][0] + "-higher seed wins!"+ str(difference) 
    else:
        sweet_sixteen.append(south[i+1])
        print south[i + 1][0]+"-lower seed wins!"+ str(difference)
print sweet_sixteen

#Advances to Sweet Sixteen
elite_eight=[]
for i in range(0, len(sweet_sixteen), 2):
    difference = (float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) )+(float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4])) + (float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]))
    if float(sweet_sixteen[i][2])-float(sweet_sixteen[i + 1][2]) +float(sweet_sixteen[i+1][4])-float(sweet_sixteen[i][4]) +float(sweet_sixteen[i][6])-float(sweet_sixteen[i + 1][6]) >0:
        elite_eight.append(sweet_sixteen[i])
        print sweet_sixteen[i][0] + "-higher seed wins!" + str(difference)
    else:
        elite_eight.append(sweet_sixteen[i+1])
        print sweet_sixteen[i + 1][0]+"-lower seed wins!"+ str(difference)
print elite_eight

#Advances to Elite Eight
final_four=[]
for i in range(0, len(elite_eight), 2):
    difference = (float(elite_eight[i][2])-float(elite_eight[i + 1][2]) )+(float(elite_eight[i+1][4])-float(elite_eight[i][4])) + (float(elite_eight[i][6])-float(elite_eight[i + 1][6]))
    if float(elite_eight[i][2])-float(elite_eight[i + 1][2]) +float(elite_eight[i+1][4])-float(elite_eight[i][4]) +float(elite_eight[i][6])-float(elite_eight[i + 1][6]) >0:
        final_four.append(elite_eight[i])
        print elite_eight[i][0] + "-higher seed wins!"+ str(difference)
    else:
        final_four.append(elite_eight[i+1])
        print elite_eight[i + 1][0]+"-lower seed wins!"+ str(difference)
print final_four

#Advances to #Advances as Regional Winner to Final Four
for i in range(0, len(final_four), 2):
    difference = (float(final_four[i][2])-float(final_four[i + 1][2]) )+(float(final_four[i+1][4])-float(final_four[i][4])) + (float(final_four[i][6])-float(final_four[i + 1][6]))
    if float(final_four[i][2])-float(final_four[i + 1][2]) +float(final_four[i+1][4])-float(final_four[i][4]) +float(final_four[i][6])-float(final_four[i + 1][6]) >0:
        Regional_winner.append(final_four[i])
        print final_four[i][0] + "-higher seed wins!"+ str(difference)
    else:
        Regional_winner.append(final_four[i+1])
        print final_four[i + 1][0]+"-lower seed wins!"+ str(difference)


#Final Four
Finals=[]
for i in range(0, len(Regional_winner), 2):
    difference = (float(Regional_winner[i][2])-float(Regional_winner[i + 1][2]) )+(float(Regional_winner[i+1][4])-float(Regional_winner[i][4])) + (float(Regional_winner[i][6])-float(Regional_winner[i + 1][6]))
    if float(Regional_winner[i][2])-float(Regional_winner[i + 1][2]) +float(Regional_winner[i+1][4])-float(Regional_winner[i][4]) +float(Regional_winner[i][6])-float(Regional_winner[i + 1][6]) >0:
        Finals.append(Regional_winner[i])
        print Regional_winner[i][0] + "-higher seed wins!"+ str(difference)
    else:
        Finals.append(Regional_winner[i+1])
        print Regional_winner[i + 1][0]+"-lower seed wins!"+ str(difference)

print Regional_winner

#Finals
for i in range(0, len(Finals), 2):
    difference = (float(Finals[i][2])-float(Finals[i + 1][2]) )+(float(Finals[i+1][4])-float(Finals[i][4])) + (float(Finals[i][6])-float(Finals[i + 1][6]))
    if float(Finals[i][2])-float(Finals[i + 1][2]) +float(Finals[i+1][4])-float(Finals[i][4]) +float(Finals[i][6])-float(Finals[i + 1][6]) >0:
        print Finals[i][0] + "-higher seed wins!"+ str(difference)
    else:
       
        print Finals[i + 1][0]+"-lower seed wins!"+ str(difference)
print Finals
