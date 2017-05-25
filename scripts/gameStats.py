from StringIO import StringIO
from pymongo import MongoClient
import pycurl
import argparse
import playerHandler
import goalieHandler
import csv
import datetime
from bson.json_util import dumps
#python gameStats.py -u http://pointstreak.com/prostats/boxscore.html?gameid=3106227 -t1 19 2 -t2 19 2 -o false -f file.csv


client = MongoClient()
db=client.gameStats
db_players=client.test

now = datetime.datetime.now().strftime("x20170523")

#handle boolean argument for OT
def getBool(arg):
	if arg.lower() in ('yes', 'true', 't', 'y', '1'):
		return True
	if arg.lower() in ('no', 'false', 'f', 'n', '0'):
		return False
	else :
		raise argparse.ArgumentTypeError('Boolean value expected')

#name on site is (last , first). Change to (first last)
def sortName(name):
	key=', '
	last, key, first = name.partition(key)
	name = str(first) + ' ' + str(last)
	return name

#return player ID 
def getId(name):
	player=dumps(db_players.playerList.find_one({"name": name}))
	userId=extract("\"id\": \"", "\"", str(player))
	if userId == "":
		return 999	
	else:
		return userId

#parse db for attribute of interest
def extract(key1, key2, val):
	before, key, after = str(val).partition(key1)
	before, key, after = after.partition(key2)
	return before



#parse command line args
parser=argparse.ArgumentParser(description='playerStats gathering')
parser.add_argument('-u', '--url', dest='url', help='url of game', required=True)
parser.add_argument('-f', '--file', dest='file', help='file name of output', required=True)
parser.add_argument('-t1', '--team1', dest='team1', nargs=2,  help='number of players, then goalies on team 1 ie -t1 19 2', required=True)
parser.add_argument('-t2', '--team2', dest='team2', nargs=2, help='number of players, then goalies on team 2 ie -t2 19 2', required=True)
parser.add_argument('-o', '--ot', type=getBool, help='was there OT? (boolean value)', default=False, required=True)

#handle args
args=parser.parse_args()


team1Players=int(args.team1[0])
team1Goalies=int(args.team1[1])
team2Players=int(args.team2[0])
team2Goalies=int(args.team2[1])
url=args.url
ot=args.ot
file=args.file

#storing players/goalies and their stats
playerMatrix=[]
goalieMatrix=[]

#perform curl of URL
storage = StringIO()
c = pycurl.Curl()
c.setopt(c.URL, url)
c.setopt(c.WRITEFUNCTION, storage.write)
c.perform()
c.close()

#store webpage html in variable
content = storage.getvalue()


#get to the players by parsing for that line
key="<!-- GET THE ROSTERS -->"
before, key, after = content.partition(key)

#get the first teams stats
playerMatrix, after = playerHandler.getPlayers(team1Players, playerMatrix, after)
goalieMatrix, after = goalieHandler.getGoalies(team1Goalies, goalieMatrix, after, ot)

#get the second teams stats
playerMatrix, after = playerHandler.getPlayers(team2Players, playerMatrix, after)
goalieMatrix, after = goalieHandler.getGoalies(team2Goalies, goalieMatrix, after, ot)



#prepare csv file, write first line
out = csv.writer(open(file, "w"), delimiter=',', quoting=csv.QUOTE_NONE)
out.writerow(["Player Name", "Goals", "Assists", "Loose Balls", "Turnovers", "Caused Turnovers", "Fantasy Points"])


#calculating player points
for i in range (0, len(playerMatrix)):
	
	playerMatrix[i][0]=sortName(playerMatrix[i][0])
	score = ((3*(int(playerMatrix[i][1]))) + 
		(1*(int(playerMatrix[i][2]))) + 
		(0.25*(int(playerMatrix[i][3])))+ 
		(-0.5*(int(playerMatrix[i][4]))) + 
		(1*(int(playerMatrix[i][5]))))
	playerMatrix[i].append(score)

	out.writerow([playerMatrix[i][0], 
		playerMatrix[i][1], 
		playerMatrix[i][2], 
		playerMatrix[i][3], 
		playerMatrix[i][4], 
		playerMatrix[i][5], 
		playerMatrix[i][6]])


	
	#get ID of player and append to player array
	playerMatrix[i].append(getId(playerMatrix[i][0]))

	#insert each into db
	result=db[now].insert({
		"name": playerMatrix[i][0],
		"fpoints": playerMatrix[i][6],
		"id": playerMatrix[i][7],
		"goals": playerMatrix[i][1],
		"assists": playerMatrix[i][2],
		"looseBalls": playerMatrix[i][3],
		"turnovers": playerMatrix[i][4],
		"causedTurnovers": playerMatrix[i][5]
				})


out.writerow(["Goalie Name", "WIN/LOSS", "GA", "Saves", "FantasyPoints"])


#calculating goalie points
for i in range(0, len(goalieMatrix)):
	score = ((-1 * (int(goalieMatrix[i][2])))+
		(0.5*(int(goalieMatrix[i][3]))))

	if goalieMatrix[i][1]=='WIN':
		score+=3

	#find each goalie in db
	#goalies already exist in DB as they collect player stats too
	#sum goalie points to his player points
	#append to matrix
	goalieMatrix[i].append(int(float(extract("fpoints\': ", ",", str(db[now].find_one({"name": goalieMatrix[i][0]})))))+score)

	#write to csv file
	out.writerow([goalieMatrix[i][0],
	goalieMatrix[i][1],
	goalieMatrix[i][2],
	goalieMatrix[i][3],
	goalieMatrix[i][4]])

	#update goalie stats in db
	result=db[now].update({
		"name": goalieMatrix[i][0]},
		{'$set': {
		"fpoints": goalieMatrix[i][4],
		"saves": goalieMatrix[i][3],
		"goalsAgainst": goalieMatrix[i][2],
		"winLoss": goalieMatrix[i][1]}})






 
