def getPlayers(teamPlayers, playerMatrix, after):
	x=len(playerMatrix)
	for i in range (0,teamPlayers):
		playerMatrix.append([])
		key="playerpage.html?"
		before, key, after = after.partition(key)

		key=">"
		before, key, after = after.partition(key)

		#now we are player 1 name
		key="<"
		before, key, after = after.partition(key)
		playerMatrix[x].append(before)

		#get goals
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		playerMatrix[x].append(before)

		#get assists
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		playerMatrix[x].append(before)

		#get points (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		#get ppg (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		#get shg (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		#get PIM (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		#get SOG (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		#get SOFF (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)


		#get LB
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		playerMatrix[x].append(before)
		#get TO
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		playerMatrix[x].append(before)
		#get CTO
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		playerMatrix[x].append(before)

		#get FO (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		x=x+1
	return playerMatrix, after