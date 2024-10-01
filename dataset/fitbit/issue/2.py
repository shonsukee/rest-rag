@shared_task
def fetch_fitbit_data(fitbit_member_id, access_token):
    '''
    Fetches all of the fitbit data for a given user
    '''
    fitbit_urls = [
        {
         'url': '/{user_id}/sleep/awakeningsCount/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'sleep-efficiency',
         'url': '/{user_id}/sleep/efficiency/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'sleep-minutes-after-wakeup',
         'url': '/{user_id}/sleep/minutesAfterWakeup/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'sleep-minutes',
         'url': '/{user_id}/sleep/minutesAsleep/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'awake-minutes',
         'url': '/{user_id}/sleep/minutesAwake/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'minutes-to-sleep',
         'url': '/{user_id}/sleep/minutesToFallAsleep/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'sleep-start-time',
         'url': '/{user_id}/sleep/startTime/date/{start_date}/{end_date}.json',
         'period': 'year'},
        {'name': 'time-in-bed',
         'url': '/{user_id}/sleep/timeInBed/date/{start_date}/{end_date}.json',
         'period': 'year'},
    ]

    # Get Fitbit member object
    fitbit_member = FitbitMember.objects.get(id=fitbit_member_id)

    oh_access_token = fitbit_member.user.get_access_token()
    fitbit_access_token = fitbit_member.get_access_token()

    # Get existing data as currently stored on OH
    fitbit_data = get_existing_fitbit(oh_access_token, fitbit_urls)

    # Set up user realm since rate limiting is per-user
    print(fitbit_member.user)
    user_realm = 'fitbit-{}'.format(fitbit_member.user.oh_id)
    rr.register_realm(user_realm, max_requests=150, timespan=3600)
    rr.update_realm(user_realm, max_requests=150, timespan=3600)

    # Get initial information about user from Fitbit
    headers = {'Authorization': "Bearer %s" % fitbit_access_token}
    query_result = requests.get('https://api.fitbit.com/1/user/-/profile.json', headers=headers).json()

    # Store the user ID since it's used in all future queries
    user_id = query_result['user']['encodedId']
    member_since = query_result['user']['memberSince']
    start_date = arrow.get(member_since, 'YYYY-MM-DD')

    # Reset data if user account ID has changed.
    if 'profile' in fitbit_data:
        if fitbit_data['profile']['encodedId'] != user_id:
            logging.info(
                'User ID changed from {} to {}. Resetting all data.'.format(
                    fitbit_data['profile']['encodedId'], user_id))
            fitbit_data = {}
            for url in fitbit_urls:
                fitbit_data[url['name']] = {}
        else:
            logging.debug('User ID ({}) matches old data.'.format(user_id))

    fitbit_data['profile'] = {
        'averageDailySteps': query_result['user']['averageDailySteps'],
        'encodedId': user_id,
        'height': query_result['user']['height'],
        'memberSince': member_since,
        'strideLengthRunning': query_result['user']['strideLengthRunning'],
        'strideLengthWalking': query_result['user']['strideLengthWalking'],
        'weight': query_result['user']['weight']
    }

    try:
        # Some block about if the period is none
        for url in [u for u in fitbit_urls if u['period'] is None]:
            if not user_id and 'profile' in fitbit_data:
                user_id = fitbit_data['profile']['user']['encodedId']

            # Build URL
            fitbit_api_base_url = 'https://api.fitbit.com/1/user'
            final_url = fitbit_api_base_url + url['url'].format(user_id=user_id)
            # Fetch the data
            r = rr.get(url=final_url,
                    headers=headers,
                    realms=["Fitbit", 'fitbit-{}'.format(fitbit_member.user.oh_id)])

            fitbit_data[url['name']] = r.json()

        #Period year URLs
        for url in [u for u in fitbit_urls if u['period'] == 'year']:
            if len(list(fitbit_data[url['name']].keys())) > 0:
                last_present_year = sorted(fitbit_data[url['name']].keys())[-1]
            else:
                last_present_year = ""

            years = arrow.Arrow.range('year', start_date.floor('year'),
                                    arrow.get())
            for year_date in years:
                year = year_date.format('YYYY')

                if year in fitbit_data[url['name']] and year != last_present_year:
                    logger.info('Skip retrieval {}: {}'.format(url['name'], year))
                    continue

                logger.info('Retrieving %s: %s', url['name'], year)
                # Build URL
                fitbit_api_base_url = 'https://api.fitbit.com/1/user'
                final_url = fitbit_api_base_url + url['url'].format(user_id=user_id,
                                                                    start_date=year_date.floor('year').format('YYYY-MM-DD'),
                                                                    end_date=year_date.ceil('year').format('YYYY-MM-DD'))
                # Fetch the data
                print(final_url)
                r = rr.get(url=final_url,
                        headers=headers,
                        realms=["Fitbit", 'fitbit-{}'.format(fitbit_member.user.oh_id)])

                fitbit_data[url['name']][str(year)] = r.json()

        # Month period URLs/fetching
        for url in [u for u in fitbit_urls if u['period'] == 'month']:
            # get the last time there was data
            if len(list(fitbit_data[url['name']].keys())) > 0:
                last_present_month = sorted(fitbit_data[url['name']].keys())[-1]
            else:
                last_present_month = ""

            months = arrow.Arrow.range('month', start_date.floor('month'),
                                    arrow.get())
            for month_date in months:
                month = month_date.format('YYYY-MM')

                if month in fitbit_data[url['name']] and month != last_present_month:
                    logger.info('Skip retrieval {}: {}'.format(url['name'], month))
                    continue

                logger.info('Retrieving %s: %s', url['name'], month)
                # Build URL
                fitbit_api_base_url = 'https://api.fitbit.com/1/user'
                final_url = fitbit_api_base_url + url['url'].format(user_id=user_id,
                                                                    start_date=month_date.floor('month').format('YYYY-MM-DD'),
                                                                    end_date=month_date.ceil('month').format('YYYY-MM-DD'))
                # Fetch the data
                r = rr.get(url=final_url,
                        headers=headers,
                        realms=["Fitbit", 'fitbit-{}'.format(fitbit_member.user.oh_id)])

                fitbit_data[url['name']][month] = r.json()

        # Update the last updated date if the data successfully completes
        fitbit_member.last_updated = arrow.now().format()
        fitbit_member.save()

    except RequestsRespectfulRateLimitedError:
        logging.info('Requests-respectful reports rate limit hit.')
        fetch_fitbit_data.apply_async(args=[fitbit_member_id, fitbit_access_token], countdown=3600)
    finally:
        replace_fitbit(fitbit_member.user, fitbit_data)