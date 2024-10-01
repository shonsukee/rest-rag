Fitbit.prototype.fetchSleepInfo = function(userId) {
	var user = this.users[userId];
	var url = "http://api.fitbit.com/1/user/-/sleep/minutesAsleep/date/today/1w.json";
	this.oauth.get(url, user.token, user.secret, function (err, data, response) {
	   var state = {};
	   try{
		state["fitbit." + userId + "." + "SleepInfo"] = JSON.parse(data);
	   } catch (e) {
		 console.log("Could not parse fitbit", url, err, data, response.statusCode);
	   }
	   if (this.debug) console.log(JSON.stringify(state, null, '  '));
	   this.emit("StateEvent", state);
	}.bind(this));
  }