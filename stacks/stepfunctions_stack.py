from aws_cdk import Stack
from constructs import Construct
from constructors.step_functions import state_functions
from constructors.step_functions import job_completion_detection
from constructors.step_functions import stepfunctions
from constructors.step_functions import functions
from constructors.step_functions import dynamodb


class StepfunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------
        # DynamoDB for Stepfunctions Callback task token
        callback_dynamodb = dynamodb.CallbackTableConstructor(
            self,
            'CallbackTableConstructors',
        )

        # --------------------------------------------------
        # AWS Lambda functions to join StepFunctions State Machine

        sfn_get_instance_id_function = state_functions.SfnGetInstanceIdFunctionConstructors(
            self,
            'SfnGetInstanceIdFunctionConstructors',
        )

        sfn_job_execute_function = state_functions.SfnJobExecuteFunctionConstructors(
            self,
            'SfnJobExecuteFunctionConstructors',
        )

        props = {
            "callback_table": callback_dynamodb.table
        }
        sfn_receive_callback_token_function = state_functions.SfnReceiveCallbackTokenConstructors(
            self,
            'SfnReceiveCallbackTokenConstructors',
            **props
        )

        # ------ job completion function
        props = {
            "callback_table": callback_dynamodb.table
        }
        job_completion_detection_function = \
            job_completion_detection.JobCompletionDetectionFunctionConstructor(
                self,
                'JobCompletionDetectionFunctionConstructor',
                **props
        )

        # --------------------------------------------------
        # AWS Step Functions
        props = {
            'get_instance_id_function': sfn_get_instance_id_function.function,
            'job_execute_function': sfn_job_execute_function.function,
            'receive_callback_token_function': sfn_receive_callback_token_function.function,
        }

        step_functions = stepfunctions.StepFunctionsConstructor(
            self,
            'StepFunctionsConstructor',
            **props,
        )

        # --------------------------------------------------
        # function to start Stepfunction
        props = {
            # 'statemachine_arn': step_functions.state_machine.state_machine_arn
            'statemachine': step_functions.state_machine
        }
        start_sfn_function = functions.FunctionConstructors(
            self,
            'StartSfnFunctionConstructors',
            **props
        )
