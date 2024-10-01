app.get('/getAllSleep', function (req, res) {
    fitbitClient.apiCall('GET', '/user/-/sleep/minutesAsleep/date/2014-04-03/max.json',
        {token: {oauth_token_secret: token.oauth_token_secret, oauth_token: token.oauth_token}},
        function(err, resp) {
            res.writeHead(200, 'application/json');
            res.end(JSON.stringify(resp));
    });
    
});
