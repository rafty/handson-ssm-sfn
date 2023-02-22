import os
import boto3
import json
import gzip
import base64
from aws_lambda_powertools import Logger
from aws_xray_sdk import core as x_ray

logger = Logger()
x_ray.patch_all()

ssm = boto3.client('ssm')
dynamo = boto3.client('dynamodb')
sfn = boto3.client('stepfunctions')

callback_table_name = os.getenv('CALLBACK_TABLE_NAME')


def get_logs_event_data(event):
    # base64 decode & decompress
    logs_data = event['awslogs']['data']
    decode_base64 = base64.b64decode(logs_data)
    decompress = gzip.decompress(decode_base64)
    data = json.loads(decompress)
    logger.info({'data:': data})

    log_group = data['logGroup']
    log_stream = data['logStream']
    messages = [event['message'] for event in data['logEvents']]

    logger.info({
        'log_group': log_group,
        'log_stream': log_stream,
        'messages': messages,
    })

    return log_group, log_stream, messages


def extruct_parameter(log_stream: str):
    """ log stream name format:
          - 'CommandID/InstanceID/PluginID/stdout'
          - 'CommandID/InstanceID/PluginID/stderr'"""
    logger.info({'log_stream:': log_stream})

    str_list = log_stream.rsplit('/')
    plugin_id = str_list[-2]
    ssm_run_command_id = str_list[-4]
    instance_id = str_list[-3]
    return plugin_id, ssm_run_command_id, instance_id


def get_callback_token(ssm_run_command_id, instance_id):

    key = {
        'ssm_run_command_id': {'S': ssm_run_command_id},  # sort key
        'instance_id': {'S': instance_id}  # partition key
    }
    resp = dynamo.get_item(TableName=callback_table_name, Key=key)

    item = resp.get('Item')
    logger.info({'item': item})

    task_token = item.get('task_token', {}).get('S', {})
    logger.info({'task_token': task_token})
    return task_token


def send_to_sfn(result, token):
    if result:
        output = json.dumps(
            {
                'result': 'SUCCESS',
                'reason': 'no error',
            }
        )
        sfn.send_task_success(
            taskToken=token,
            output=output
        )
        print('Success Callback called')
    else:
        output = json.dumps(
            {
                'result': 'ERROR',
                'reason': 'some error',
            }
        )
        sfn.send_task_failure(
            taskToken=token,
            output=output
        )
        print('Success Callback called')


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):

    try:
        log_group, log_stream, messages = get_logs_event_data(event)
        plugin_id, ssm_run_command_id, instance_id = extruct_parameter(log_stream)

        logger.info({'plugin_id': plugin_id,
                     'ssm_run_command_id': ssm_run_command_id,
                     'instance_id': instance_id})

        if plugin_id not in ['aws-runShellScript']:
            logger.info(f'Not Support Plugin: {plugin_id}')
            return

        task_token = get_callback_token(ssm_run_command_id, instance_id)

        # Todo:
        #  logsのメッセージを判断して、成功か失敗をStateMachineに通知する
        #  Handsonのためここでは成功の通知のみ
        send_to_sfn(result=True, token=task_token)

        return

    except Exception as e:
        logger.exception(e)
        raise e
