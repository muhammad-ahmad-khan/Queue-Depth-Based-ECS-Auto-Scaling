import boto3
import dateutil
from datetime import date, timedelta, datetime


def lambda_handler(event, context):
    cw_client = boto3.client('cloudwatch')
    ecs_client = boto3.client('ecs')
    cluster_name = event["cluster_name"]
    service_name = event['service_name']
    mq_cluster_name = event["mq_cluster_name"]
    mq_queue_name = event["mq_queue_name"]
    acceptable_latency = (event["acceptable_latency"])
    time_process_per_message = (event["time_process_per_message"])
    queue_attribute_calculation(cw_client, ecs_client, cluster_name, service_name, mq_cluster_name, mq_queue_name, acceptable_latency,
                                time_process_per_message)


def queue_attribute_calculation(cw_client, ecs_client, cluster_name, service_name, mq_cluster_name, mq_queue_name, acceptable_latency,
                                time_process_per_message):
    response = ecs_client.describe_services(
        cluster=cluster_name, services=[service_name])
    running_task_count = response['services'][0]['runningCount']
    print("Running Task: " + str(running_task_count))

    yesterday = date.today() - timedelta(days=2)
    tomorrow = date.today() + timedelta(days=1)
    response = cw_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'mq1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/AmazonMQ',
                        'MetricName': 'MessageReadyCount',
                        'Dimensions': [
                            {
                                'Name': 'Broker',
                                'Value': mq_cluster_name
                            },
                            {
                                'Name': "VirtualHost",
                                'Value': "/"
                            },
                            {
                                'Name': "Queue",
                                'Value': mq_queue_name
                            }
                        ]
                    },
                    'Period': 1,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
            },
        ],
        StartTime=datetime(yesterday.year, yesterday.month, yesterday.day),
        EndTime=datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    )

    queue_size = response['MetricDataResults'][0]['Values'][0]

    print("Running Task: " + str(running_task_count))
    print("Queue Message Count (per second): " + str(queue_size))

    """
    Backlog Per Capacity Unit = Queue Size (MessageReadyCount) / Running Capacity of ECS Task Count
    """
    try:
        backlog_per_capacity_unit = int(int(queue_size) / running_task_count)
    except ZeroDivisionError as err:
        print('Handling run-time error:', err)
        backlog_per_capacity_unit = 0
    print("Backlog Per Capacity Unit: " + str(backlog_per_capacity_unit))

    """
    Acceptable backlog per capacity unit = Acceptable Message Processing Latency (seconds) / Average time to Process a Message each Task (seconds)
    """
    acceptablebacklogpercapacityunit = float(
        (int(acceptable_latency) / float(time_process_per_message)))
    print("Acceptable backlog per capacity unit: " +
          str(acceptablebacklogpercapacityunit))

    putMetricToCW(cw_client, 'AmazonMQ', mq_cluster_name, 'Queue', mq_queue_name, 'MessageReadyCount', int(queue_size),
                  'Queue Based Scaling Metrics')
    putMetricToCW(cw_client, 'AmazonMQ', mq_cluster_name, 'Queue', mq_queue_name, 'BackLogPerCapacityUnit', backlog_per_capacity_unit,
                  'Queue Based Scaling Metrics')
    putMetricToCW(cw_client, 'AmazonMQ', mq_cluster_name, 'Queue', mq_queue_name, 'AcceptableBackLogPerCapacityUnit', acceptablebacklogpercapacityunit,
                  'Queue Based Scaling Metrics')


def putMetricToCW(cw, dimension_name, dimension_value, dimension_sub_attribute_name, dimension_sub_attribute_value, metric_name, metric_value, namespace):
    cw.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    },
                    {
                        'Name': dimension_sub_attribute_name,
                        'Value': dimension_sub_attribute_value
                    }
                ],
                'Timestamp': datetime.now(dateutil.tz.tzlocal()),
                'Value': metric_value
            }
        ]
    )
