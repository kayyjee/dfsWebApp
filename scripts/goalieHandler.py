def getGoalies(teamGoalies, goalieMatrix, after, ot):
	y=len(goalieMatrix)

	for i in range (0,teamGoalies):

		#get the goalies
		goalieMatrix.append([])
		key="playerpage.html"
		before, key, after = after.partition(key)
		key=">"
		before, key, after = after.partition(key)
		#get goalie name
		key="<"
		before, key, after = after.partition(key)
		goalieMatrix[y].append(before)


		#Goalie WIN/LOSS
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		if (before != '&nbsp;') and (before != ''):
			goalieMatrix[y].append(before)
		else :
			goalieMatrix[y].append(0)

		#Goalie MIN (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		#Goalie GA
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		if before != '&nbsp;':
			goalieMatrix[y].append(before)
		else :
			goalieMatrix[y].append(0)

		#Goalie SOG (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		#Goalie SAVES
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)
		if before != '&nbsp;':
			goalieMatrix[y].append(before)
		else :
			goalieMatrix[y].append(0)

		#Goalie SV1 (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		#Goalie SV2 (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		#Goalie SV3 (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		#Goalie SV4 (not used)
		key="<td>"
		before, key, after = after.partition(key)
		key="<"
		before, key, after = after.partition(key)

		#if OT, get OT Saves (not used)
		if (ot== True):
			#Goalie SVOT
			key="<td>"
			before, key, after = after.partition(key)
			key="<"
			before, key, after = after.partition(key)

		y=y+1
	return goalieMatrix, after