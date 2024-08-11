import boto3
import os
import sys

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def publish_ontime_arr_rate(ontime_arr_rate:str):
    sns_client = boto3.client('sns')
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=ontime_arr_rate
    )

if __name__ == '__main__':
    ontime_arr_rate_str = sys.stdin.read().strip()
    publish_ontime_arr_rate(ontime_arr_rate_str)
