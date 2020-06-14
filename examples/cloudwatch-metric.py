# Pretty rough script that sends the information from all your sensors
# to AWS CloudWatch as a single metrics API call. You would run this as
# a cron job every minute.
#
# I'm assuming you have some basic AWS knowledge and know how to configure
# your environment with credentials to send data to AWS.
#
# The most basic IAM policy you need is something like this:
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "VisualEditor0",
#             "Effect": "Allow",
#             "Action": [
#                 "cloudwatch:PutMetricData"
#             ],
#             "Resource": "*"
#         }
#     ]
# }

from w1thermsensor import W1ThermSensor
import boto3

# Modify these values for your setup
namespace = "Climate Logging"
location = "Workshop"
sensor_names = {"xxxxxxxxxxxx": "Indoor", "yyyyyyyyyyyy": "Outdoor"}

metrics = []
for sensor in W1ThermSensor.get_available_sensors():
    print(
        'Sensor "%s" has temperature %.2f'
        % (sensor_names[sensor.id], sensor.get_temperature())
    )
    metrics.append(
        {
            "MetricName": "Temperature",
            "Dimensions": [
                {"Name": "Location", "Value": location},
                {"Name": "Placement", "Value": sensor_names[sensor.id]},
            ],
            "Unit": "None",
            "Value": sensor.get_temperature(),
        }
    )

# Send the metrics to CloudWatch
client = boto3.client("cloudwatch")
response = client.put_metric_data(Namespace=namespace, MetricData=metrics)
