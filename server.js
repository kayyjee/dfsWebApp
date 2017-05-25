var bcrypt = require('bcryptjs');
var jwt = require('jwt-simple');
var bodyParser = require('body-parser');
var MongoClient = require('mongodb').MongoClient;
var MongoClientResults = require('mongodb').MongoClient;
var ObjectID = require('mongodb').ObjectID;
var express = require('express');
var app = express();
var server=require('http').createServer(app);
var io = require('socket.io').listen(server);
users=[];
connections=[];

var db = null;
var JWT_SECRET = 'SECRET_KEY'

MongoClient.connect("mongodb://localhost:27017/test", function(err, dbconn){
	if(!err){
		console.log("we are now connected to main db");
		db = dbconn;

	}
});
MongoClientResults.connect("mongodb://localhost:27017/userResults", function(err, dbconn){
	if(!err){
		console.log("we are now connected to results db");
		dbResults = dbconn;
	}
});


app.use(express.static('public'));
//app.use(bodyParser.urlencoded({ extended: false}))
app.use(bodyParser.json());


var numUsers=0;

server.listen(process.env.PORT || 3000);









//Chatroom Handling of Sockets
io.sockets.on('connection', function(socket){
	connections.push(socket);
	
	socket.on('disconnect', function(data){
		username=socket.username
		connections.splice(connections.indexOf(socket), 1);
		
		if (username!=null){	
		numUsers--;
		io.sockets.emit('user disconnected', {numUsers, username});
		socket.username=null;
		};
	});

	socket.on('send message', function(data){
		io.sockets.emit('new message', {data});
		console.log(socket)

	});

	socket.on('new user', function(data){
		numUsers++;
		socket.username=data;
		io.sockets.emit('user joined', {data, numUsers});
	});
	
	socket.on('user logout', function (data){
		username=socket.username
		if (username!=null){	
			numUsers--;
			io.sockets.emit('user disconnected', {numUsers, username});
			socket.username=null;
		}
	});

});









//hard coding the next day for now for testing
function getNextDay(){
	return "05/23/2017"
}

//Called upon entering the site. Returns some information for client to store as root variables
app.get('/schedule', function(req, res, next){
	var NEXT_DAY=getNextDay();

	db.collection('schedule', function(err, scheduleCollection){
		scheduleCollection.find({date: NEXT_DAY}).limit(1).next(function(err, teamsToday){
			nextGameTime = NEXT_DAY + " " + teamsToday.time
			
			return res.json({nextGameTime: nextGameTime, numUsers: numUsers});
		
		});
	});
});







//pick players page
//return the player's that play that day
//if user team exists, do not allow for duplicates
app.put('/playerList', function(req, res, next) {
	var NEXT_DAY = getNextDay();
	
	//search schedule db for teams that play that day (or the next closest gameday)
	db.collection('schedule', function(err, scheduleCollection){
		scheduleCollection.find({date: NEXT_DAY}).limit(1).next(function(err, playersToday){
			
			if (playersToday == null){
				teamsToday = null;
				return;
			}
			else{
				
				teamsToday = playersToday.teams;
				
				if (teamsToday == null){
					return
					
				}
			}
		});
	});
	todaysPlayers = [];
	//checking if user has an existing team
	db.collection('teams', function(err, players_dbvalues){
		//finding db team that matches username and date
		players_dbvalues.find({username: req.body.username, 
		theDate: NEXT_DAY}).limit(1).next(function(err, teamPlayers){

			//find all players that play today
			db.collection('playerList', function(err, players_dbvalues){
				players_dbvalues.find().toArray(function(err, players){
					
					//iterate through each player
					for (i=0; i<players.length; i++){
						//add players that match a team that plays today
						for (j=0; j<teamsToday.length; j++){
							if (players[i].team == teamsToday[j]){
								todaysPlayers.push(players[i]);	
							}
						}	
					}			
					//if user has not yet set a team, return all players
					if (teamPlayers == null){
						
						return res.json(todaysPlayers);	
					}
					else{
						var existingPlayerIds=[];
						existingPlayerIds.push(teamPlayers.player1);
						existingPlayerIds.push(teamPlayers.player2);
						existingPlayerIds.push(teamPlayers.player3);
						existingPlayerIds.push(teamPlayers.player4);
						existingPlayerIds.push(teamPlayers.player5);
						//create a new array consisting of only players that are not duplicates
						var playersNotOnTeam =[];
						//remove all the players that match the id in team players
						for (i=0; i<todaysPlayers.length; i++){
							if ((todaysPlayers[i].id != existingPlayerIds[0])&&
								(todaysPlayers[i].id != existingPlayerIds[1])&&
								(todaysPlayers[i].id != existingPlayerIds[2])&&
								(todaysPlayers[i].id != existingPlayerIds[3])&&
								(todaysPlayers[i].id != existingPlayerIds[4])){
								
								playersNotOnTeam.push(todaysPlayers[i]);
							}
						}			
						return res.json(playersNotOnTeam);
					}
				});
			});	
		});
	});		
});
						










//method to return the player's team based on username and date
//display their team on the homepage
app.put('/teamList', function(req, res, next) {
	var NEXT_DAY=getNextDay();

	db.collection('teams', function(err, players_dbvalues){
		//finding db team that matches username and date
		players_dbvalues.find({username: req.body.username, 
		theDate: NEXT_DAY}).limit(1).next(function(err, players){

			//if no team, return an empty json array
			if (players == null){
				var playersArray = [];
				return res.json(playersArray);
			}
			else{			
				//finding players that match playerID's 
	 			db.collection('playerList', function(err, playerList){
	 				var teamPlayers=[]
	 				playerList.find({id: players.player1}).next(function(err, player){
	 					teamPlayers.push(player);
	 				});
	 				playerList.find({id: players.player2}).next(function(err, player){
	 					teamPlayers.push(player);
		 				});
		 			playerList.find({id: players.player3}).next(function(err, player){
	 					teamPlayers.push(player);
	 					});
		 			playerList.find({id: players.player4}).next(function(err, player){
	 					teamPlayers.push(player);
	 				});
	 				playerList.find({id: players.player5}).next(function(err, player){

	 					teamPlayers.push(player);
	 					return res.json(teamPlayers);
	 				});
				});
	 		}
		});
	});
});





//user is going to results page 
app.put('/users/results', function(req, res, next) {
	var resultsCollection=dbResults.collection(String(req.body.username));

	resultsCollection.find().toArray(function(err, results){
		var userResults=results
		return res.json(userResults);	
	});
});
	




//User is logging-in
app.put('/users/signin', function(req, res, next) {
	var NEXT_DAY=getNextDay();

	db.collection('users', function(err, usersCollection){
		//Username does not exist
		usersCollection.findOne({username: req.body.username}, function(err, user){
			if (user == null){
				return res.status(400).send();
			}
			else{
				//username exists,
				//compare password with hash
				bcrypt.compare(req.body.password, user.password, function(err,result){
					if (result) {
						var token = jwt.encode(user, JWT_SECRET);
						var teamChoice = user.teamChoice;
						//username password correct, check if user has a team for today.
						db.collection('teams', function(err, players_dbvalues){
							players_dbvalues.find({username: req.body.username, 
							theDate: NEXT_DAY}).limit(1).next(function(err, team){
								var hasTeam=false;
								if (team == null){
									return res.json({token: token, hasTeam: hasTeam, teamChoice: teamChoice});
								}
								else{

									hasTeam=true;
									return res.json({token: token, hasTeam: hasTeam, teamChoice: teamChoice});
								}
							});
						});
					}	
					else {
						return res.status(400).send();
					};
				});
			};	
		});
	});	
});

//User is submitting the team
app.post('/team/submit', function(req,res, next){
	var NEXT_DAY=getNextDay();

	db.collection('teams', function(err, teamCollection){
		//check if user already has a team for today 
		teamCollection.findOne({username: req.body.username, theDate: NEXT_DAY}, function(err, existingTeam){		
			//if they don't, create a new team
			if (existingTeam == null) {
				var team = {
					username: req.body.username,
					theDate: NEXT_DAY,
					player1: req.body.player1,
					player2: req.body.player2,
					player3: req.body.player3,
					player4: req.body.player4,
					player5: req.body.player5,
				};
				teamCollection.insert(team);
				return res.status(200).send();
			}
			//if they already have a team, update the team's players
			else {
				teamCollection.update({username: req.body.username, theDate: NEXT_DAY},{ $set: 
					{player1: req.body.player1,
					player2: req.body.player2,
					player3: req.body.player3,
					player4: req.body.player4,
					player5: req.body.player5}}, 
					function(err, result){
						return res.status(200).send();
					});
			}	
		});
	});
});


//User is signing-up
app.post('/users', function(req, res, next) {
	db.collection('users', function(err, usersCollection){
		//Check if username is taken
		usersCollection.findOne({username: req.body.username}, function(err, user){
			if (user != null){
				return res.status(400).send("Sorry, that username is already taken!");
			}
			else{
				//check password requirements
				if ((req.body.password == undefined) || (req.body.password == "") || (req.body.password.length < 5)){
					return res.status(400).send("Your password must be at least 5 characters");
				}
				else {
					bcrypt.genSalt(10, function(err, salt){
						bcrypt.hash(req.body.password, salt, function(err, hash){
							var newUser = {
								username: req.body.username,
								password: hash,
								teamChoice: req.body.teamChoice
							};
							usersCollection.insert(newUser, {w:1}, function(err){
								return res.status(200).send();
							});
						});
					});
				}
			}
		});
	});
});	




app.post('/players', function(req, res, next) {
	var token = req.headers.authorization;
	var user = jwt.decode(token, JWT_SECRET);
	db.collection('testCollection', function(err, players_dbvalues){
		var newPlayer= {
			text: req.body.newPlayer,
			user: user._id,
			username: user.username
		};

		if (req.body.newPlayer.length < 5){
			return res.status(400).send('not long enough');
		}
		players_dbvalues.insert(newPlayer, {w:1}, function(err){
			return res.send();
		});
	});
});












