def main() -> None:
    logger.info(f"Startup: {USER_AGENT}")
    url = f"https://api.switch-bot.com/v1.0/devices/{DEVID}/status"
    headers = {'Authorization': APIKEY}
    influxClient = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)  # noqa: E501
    write_api = influxClient.write_api(write_options=SYNCHRONOUS)
    while True:
        (deg_f, rel_hum) = read_sensor(url, headers)
        record = [
            {
                "measurement": INFLUX_MEASUREMENT_NAME,
                "fields": {
                    "degF": deg_f,
                    "rH": rel_hum
                }
            }
        ]
        write_api.write(bucket=INFLUX_BUCKET, record=record)
        sleep(SLEEPTIME)
