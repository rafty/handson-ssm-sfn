import aws_cdk
from constructs import Construct
from aws_cdk import Duration
from aws_cdk import aws_stepfunctions
from aws_cdk import aws_stepfunctions_tasks

"""
stepfunction.start_execution() -> input_json

{
  "input": {
    "event_id": "0e439f7e76c742a5997224dd4dbd7890",
    "order_id": "8a4347b048034e80bfa45a5d70c8f301",
    "channel": "OrderCreated"
  },
  "inputDetails": {
    "truncated": false
  },
  "roleArn": "arn:aws:iam::338456725408:role/OrderServiceStack-CreateOrderSagaConstructorCreate-YLDY0HX8FOFX"
}
"""


class StepFunctionsConstructor(Construct):

    def __init__(self, scope: Construct, id: str, **kwargs: dict) -> None:
        super().__init__(scope, id)

        # ------------------------------------------------------
        #  functions to join state machine
        self.get_instance_id_function = kwargs.get('get_instance_id_function')
        self.job_execute_function = kwargs.get('job_execute_function')
        self.receive_callback_token_function = kwargs.get('receive_callback_token_function')
        # self.job_completion_detection_function = kwargs.get('job_completion_detection_function')

        # -----------------------------------------------------
        # tasks
        """task生成の順番に注意する。(task catchで後続のtaskを利用するため)"""

        # --------- Fail State and Succeed State of StepFunctions ----------
        self.sfn_fail_task = aws_stepfunctions.Fail(self, 'SfnFailState', comment='failed.')
        self.sfn_succeed_task = aws_stepfunctions.Succeed(
                                                    self, 'SfnSucceedState', comment='succeeded.')
        # --------- Custom Task --------------------
        self.get_instance_id_task = self.task_get_instance_id()
        self.job_execute_task = self.task_job_execute()
        self.receive_callback_token_task = self.task_receive_callback_token()

        # -----------------------------------------------------
        # State Machine
        self.state_machine = self.create_state_machine()

        # Todo: state machineから直接callしてる場合、grantは必要ない(たぶん)
        #  しかし、job_completion_detection()などのCloudwatchLogsトリガのLambdaの場合はgrantが必要！！
        # self.state_machine.grant_task_response(self.receive_callback_token_function)

    # -------------------------------------------------------
    # State Machine
    # -------------------------------------------------------
    def create_state_machine(self):
        state_machine = aws_stepfunctions.StateMachine(
            self,
            'SsmHandsonStateMachine',
            state_machine_name='handson_sfn',
            definition=self.create_handson_definition(),
            timeout=Duration.minutes(60),
            tracing_enabled=True)
        return state_machine

    # -------------------------------------------------------
    # task definition
    # -------------------------------------------------------
    # def create_handson_definition(self):
    #     definition = aws_stepfunctions.Chain\
    #         .start(self.get_instance_id_task)\
    #         .next(self.job_execute_task)\
    #         .next(self.receive_callback_token_task)\
    #         .next(self.sfn_succeed_task)
    #
    #     return definition
    def create_handson_definition(self):
        definition = aws_stepfunctions.Chain\
            .start(self.get_instance_id_task)\
            .next(self.job_execute_task)\
            .next(self.receive_callback_token_task)\
            .next(
                aws_stepfunctions.Choice(self, 'ChoiceCallBackResult')
                .when(
                    aws_stepfunctions.Condition.string_equals(
                        '$.receive_callback_token_result.result', 'SUCCESS'),
                    next=self.sfn_succeed_task
                )
                .when(
                    aws_stepfunctions.Condition.string_equals(
                        '$.receive_callback_token_result.result', 'ERROR'),
                    next=self.sfn_fail_task
                )
                .otherwise(
                    self.sfn_fail_task
                )
            )
        return definition

    # -------------------------------------------------------
    # tasks
    # -------------------------------------------------------
    def task_get_instance_id(self):
        # ------------------------ payload ----------------------------
        task_context = {
            "state_machine": "SsmHandson",
            "action": "GET_INSTANCE_ID"
        }
        payload = aws_stepfunctions.TaskInput.from_object({
                # "order_id.$": "$.order_id",  # Todo: delete
                "tag.$": "$.tag",  # sfn start_execution()で指定するinput
                "task_context": aws_stepfunctions.TaskInput.from_object(task_context)
            })

        task = aws_stepfunctions_tasks.LambdaInvoke(
            self,
            'TaskGetInstanceId',
            lambda_function=self.get_instance_id_function,
            payload=payload,
            result_path='$.get_instance_result',  # Attention: $にするとinputが上書きされる
            output_path='$')

        task.add_catch(self.sfn_fail_task,
                       errors=[
                           'InstanceNotFoundException',
                       ],
                       result_path='$.error_info')

        return task

    def task_job_execute(self):
        # ------------------------ payload ----------------------------
        task_context = {
            "state_machine": "SsmHandson",
            "action": "JOB_EXECUTE"
        }
        payload = aws_stepfunctions.TaskInput.from_object({
            "instance_id.$": "$.get_instance_result.Payload.instance_id",
            "task_context": aws_stepfunctions.TaskInput.from_object(task_context)
        })
        # Todo: (注)パスを使用して値が選択されるキーと値のペアの場合、キー名は .$ で終わる必要があります。
        # ------------------------ payload ----------------------------

        task = aws_stepfunctions_tasks.LambdaInvoke(
            self,
            'TaskJobExecute',
            lambda_function=self.job_execute_function,
            payload=payload,
            result_path='$.job_execute_result',  # 注意: $にするとinputが上書きされる。
            output_path='$')

        task.add_catch(self.sfn_fail_task,
                       errors=[aws_stepfunctions.Errors.ALL],
                       result_path='$.error_info')

        return task

    def task_receive_callback_token(self):
        # ------------------------ payload ----------------------------
        task_context = {
            "state_machine": "SsmHandson",
            "action": "RECEIVE_CALLBACK_TOKEN"
        }
        payload = aws_stepfunctions.TaskInput.from_object({
            'instance_id.$': '$.get_instance_result.Payload.instance_id',
            'command_id.$': '$.job_execute_result.Payload.command_id',
            'task_context': aws_stepfunctions.TaskInput.from_object(task_context),
            'task_token': aws_stepfunctions.JsonPath.task_token,
        })
        # ------------------------ payload ----------------------------

        task = aws_stepfunctions_tasks.LambdaInvoke(
            self,
            'TaskReceiveCallbackToken',
            lambda_function=self.receive_callback_token_function,
            integration_pattern=aws_stepfunctions.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=payload,
            result_path='$.receive_callback_token_result',  # 注意: $にするとinputが上書きされる。
            output_path='$',
            timeout=Duration.minutes(30)  # 30分でタイムアウトする!!
        )

        # task.add_catch(self.sfn_fail_task,
        #                errors=[aws_stepfunctions.Errors.ALL],
        #                result_path='$.error_info')

        return task
