class UserTokensController < ApplicationController
    # GET /user_tokens
    # GET /user_tokens.json

    MY_CONSUMER_KEY = '82b31f0916944d2880bd07f1261d0f3d'
    MY_CONSUMER_SECRET = '55fb3407963e47f8a8c8f2b8f606f358'
    REQUEST_TOKEN_URL = 'http://api.fitbit.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'http://api.fitbit.com/oauth/access_token'
    AUTHORIZE_URL = 'http://api.fitbit.com/oauth/authorize'

    def index
        @user_tokens = UserToken.all

        respond_to do |format|
            format.html # old_index.html.erb
            format.json { render json: @user_tokens }
        end
    end

    def init # We go here when Fitbit redirects back to us. Two params. oauth_token and oauth_verifier
        # We should have a record with the oauth_token in UserToken
        token = params["oauth_token"]
        verifier = params["oauth_verifier"]
        @user_token = UserToken.where(:token => token).first
        client = Fitgem::Client.new(:consumer_key => MY_CONSUMER_KEY, :consumer_secret => MY_CONSUMER_SECRET)
        access_token = client.authorize(@user_token.token, @user_token.secret, { :oauth_verifier => verifier })
        @user_token.final_secret = access_token.secret
        @user_token.final_token = access_token.token
        @user_token.save
        @user_data = client.user_info['user']
        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @user_token }
        end
    end

    # GET /user_tokens/1
    # GET /user_tokens/1.json
    def show
        @client = basic_connect
        @user_info = @client.user_info['user']
        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @user_token }
        end
    end

    def show_activities
        @client = basic_connect
        @activities = @client.activities
        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @user_token }
        end
    end

    def show_activity
        @client = basic_connect
        @activity = @client.activity params[:activity_id]
        logger.debug @activity
        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @user_token }
        end
    end

    def show_activity_statistics
        @client = basic_connect
        @activity_statistics = @client.activity_statistics
        logger.debug @activity_statistics
        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @user_token }
        end
    end

    def show_activities_on_date
        @client = basic_connect
        @activities_on_date = @client.activities_on_date Time.now
        logger.debug @activities_on_date
        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @user_token }
        end
    end


    # GET /user_tokens/new
    # GET /user_tokens/new.json
    def new
        @user_token = UserToken.new
        client = Fitgem::Client.new(:consumer_key => MY_CONSUMER_KEY, :consumer_secret => MY_CONSUMER_SECRET)
        request_token = client.request_token
        @user_token.request_token = request_token
        @user_token.token = request_token.token
        @user_token.secret = request_token.secret
        @user_token.save
        @auth_url = "http://www.fitbit.com/oauth/authorize?oauth_token=#{@user_token.token}"

        respond_to do |format|
            format.html # show.html.erb
            format.json { render json: @dashboard }
        end
    end

    # GET /user_tokens/1/edit
    def edit
        @user_token = UserToken.find(params[:id])
    end

    # POST /user_tokens
    # POST /user_tokens.json
    def create
        @user_token = UserToken.new(params[:user_token])

        respond_to do |format|
            if @user_token.save
                format.html { redirect_to @user_token, notice: 'User token was successfully created.' }
                format.json { render json: @user_token, status: :created, location: @user_token }
            else
                format.html { render action: "new" }
                format.json { render json: @user_token.errors, status: :unprocessable_entity }
            end
        end
    end

    # PUT /user_tokens/1
    # PUT /user_tokens/1.json
    def update
        @user_token = UserToken.find(params[:id])

        respond_to do |format|
            if @user_token.update_attributes(params[:user_token])
                format.html { redirect_to @user_token, notice: 'User token was successfully updated.' }
                format.json { head :ok }
            else
                format.html { render action: "edit" }
                format.json { render json: @user_token.errors, status: :unprocessable_entity }
            end
        end
    end

    # DELETE /user_tokens/1
    # DELETE /user_tokens/1.json
    def destroy
        @user_token = UserToken.find(params[:id])
        @user_token.destroy

        respond_to do |format|
            format.html { redirect_to user_tokens_url }
            format.json { head :ok }
        end
    end

    private
    def basic_connect #Fix shortly to look at user_tokens
        @oa = {
                 :consumer_key => '82b31f0916944d2880bd07f1261d0f3d',
                 :consumer_secret => '55fb3407963e47f8a8c8f2b8f606f358',
                 :token => 'e7ed5916b0053db9d06bd6b29cbbd2a5',
                 :secret => '3094fc97cf7381ad819a95e69c61f33d',
                 :user_id => '22D339'
         }
         client = Fitgem::Client.new(@oa)
         access_token = client.reconnect(@oa[:token], @oa[:secret])
        client
    end
end