class DashboardsController < ApplicationController
	before_filter :authenticate_user!
	def index

	end

	def show
		consumer = OAuth::Consumer.new(ENV['appid'], ENV['appsecret'], site: "https://api.fitbit.com")
		token = OAuth::AccessToken.from_hash(consumer, { oauth_token: current_user.token, oauth_token_secret: current_user.secret })

		#Get user info
		response = token.get("https://api.fitbit.com/1/user/-/profile.json")
		@json = JSON.parse(response.body)
		@name=@json['user']['displayName']


		#Get goals
		json = JSON.parse(token.get('http://api.fitbit.com/1/user/-/activities/goals/daily.json').body)
		step_goal=json['goals']['steps']

		#get current date
		time= Time.now
		cur_date=time.strftime("%Y-%m-%d")

		#------ Override for testing ------ 
		#cur_date="2014-03-09"
		#-------------------------------

		json = JSON.parse(token.get('http://api.fitbit.com/1/user/-/activities/date/' + cur_date + '.json').body)
		cur_steps=json['summary']['steps']


		cur_fairly_active= json['summary']['fairlyActiveMinutes']
		cur_lightly_active= json['summary']['lightlyActiveMinutes']
		cur_very_active= json['summary']['veryActiveMinutes']
		cur_sedentary_mins= json['summary']['sedentaryMinutes']


		#we should check if greater than 1
		@steps_remain= step_goal-cur_steps
		@steps = cur_steps


		last7= get_last7_steps(cur_date,token)	

		@last7=last7
		@last7_sleep= get_last7_sleep(cur_date,token)


		@yesterday_steps=Integer(@last7.values[5])
		delta = @steps-@yesterday_steps

		if delta > 1
			@delta="You walked " + delta.to_s + " more steps than yesterday"
		else
			delta+1
			delta=delta.abs
			@delta="You need " + delta.to_s  + " more steps to beat yesterdays count"
		end

		if cur_steps > step_goal
			@completeGoal="You beat today's goal"
		else
			stepsLeft= step_goal-cur_steps
			@completeGoal="You have " + stepsLeft.to_s + " to go!"
		end

		bestDay=""
		bestValue=0
		totalStep=0
		last7.each do |key, value|
			totalStep=totalStep + value.to_i
			if bestValue < value.to_i
				bestValue=value.to_i
				bestDay=key
			end
		end
		@bestDay= bestDay
		@bestValue=bestValue
		@totalStep=totalStep


	end


	def get_last7_steps(date,token)
		cur_date= date
		json=JSON.parse(token.get('http://api.fitbit.com/1/user/-/activities/steps/date/' + cur_date + '/7d.json').body)
		arr=Hash.new
		for i in (0..6)
			date= json["activities-steps"][i]["dateTime"]
			steps=json["activities-steps"][i]["value"]
			arr[date] = steps
			end
		return arr
	end


	def get_last7_sleep(date,token)
		cur_date= date
		json=JSON.parse(token.get('http://api.fitbit.com/1/user/-/sleep/minutesAsleep/date/'+ cur_date +'/7d.json').body)
		arr=Hash.new
		for i in (0..6)
			date= json["sleep-minutesAsleep"][i]["dateTime"]
			steps=json["sleep-minutesAsleep"][i]["value"]
			arr[date] = steps
			end
		return arr
	end	


end