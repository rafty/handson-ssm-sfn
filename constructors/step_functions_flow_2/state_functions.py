import aws_cdk
from constructs import Construct
from aws_cdk import aws_lambda
from aws_cdk import aws_sam
from aws_cdk import aws_iam
from aws_cdk import Aws
from aws_cdk import aws_dynamodb


class SfnGetInstanceIdFunctionConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.function = self.create_function()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'SfnGetInstanceIdFunction',
            function_name='sfn_get_instance_id_2',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('constructors/step_functions_flow_2/functions_of_statemachine/get_instance_id'),
            timeout=aws_cdk.Duration.seconds(amount=60),
            tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
            layers=[self.lambda_powertools()],  # for X-Ray SDK
            environment={}
        )

        function.add_to_role_policy(self.ec2_policy_statement())

        return function

    @staticmethod
    def ec2_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('ec2:DescribeInstances')
        policy_statement.add_all_resources()
        policy_statement.effect = aws_iam.Effect.ALLOW
        # policy_statement.sid = ''
        return policy_statement

    def lambda_powertools(self):
        power_tools_layer = aws_sam.CfnApplication(
            scope=self,
            id='AWSLambdaPowertoolsLayer',
            location={
                'applicationId': ('arn:aws:serverlessrepo:eu-west-1:057560766410'
                                  ':applications/aws-lambda-powertools-python-layer'),
                'semanticVersion': '2.6.0'
            }
        )
        power_tools_layer_arn = power_tools_layer.get_att('Outputs.LayerVersionArn').to_string()
        power_tools_layer_version = aws_lambda.LayerVersion.from_layer_version_arn(
                scope=self,
                id='AWSLambdaPowertoolsLayerVersion',
                layer_version_arn=power_tools_layer_arn)
        return power_tools_layer_version


class SfnJobExecuteFunctionConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.function = self.create_function()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'SfnJobExecuteFunction',
            function_name='sfn_job_execute_2',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('constructors/step_functions_flow_2/functions_of_statemachine/job_execute'),
            timeout=aws_cdk.Duration.seconds(amount=60),
            tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
            layers=[self.lambda_powertools()],  # for X-Ray SDK
            environment={}
        )

        function.add_to_role_policy(self.ssm_policy_statement())

        return function

    @staticmethod
    def ssm_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('ssm:SendCommand')
        policy_statement.add_actions('ssm:GetCommandInvocation')
        policy_statement.add_actions('ssm:ListCommandInvocations')
        policy_statement.add_all_resources()
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.sid = 'SsmHandsOn'
        return policy_statement

    def lambda_powertools(self):
        power_tools_layer = aws_sam.CfnApplication(
            scope=self,
            id='AWSLambdaPowertoolsLayer',
            location={
                'applicationId': ('arn:aws:serverlessrepo:eu-west-1:057560766410'
                                  ':applications/aws-lambda-powertools-python-layer'),
                'semanticVersion': '2.6.0'
            }
        )
        power_tools_layer_arn = power_tools_layer.get_att('Outputs.LayerVersionArn').to_string()
        power_tools_layer_version = aws_lambda.LayerVersion.from_layer_version_arn(
                scope=self,
                id='AWSLambdaPowertoolsLayerVersion',
                layer_version_arn=power_tools_layer_arn)
        return power_tools_layer_version


class SfnReceiveCallbackTokenConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.callback_table: aws_dynamodb.Table = kwargs.get('callback_table')
        self.function = self.create_function()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'SfnJobExecuteFunction',
            function_name='sfn_receive_callback_token',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('constructors/step_functions_flow_2/functions_of_statemachine/recieve_callback_token'),
            timeout=aws_cdk.Duration.seconds(amount=60),
            tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
            layers=[self.lambda_powertools()],  # for X-Ray SDK
            environment={
                'CALLBACK_TABLE_NAME': self.callback_table.table_name
            }
        )

        self.callback_table.grant_read_write_data(function)
        # function.add_to_role_policy(self.sfn_policy_statement())

        return function

    # @staticmethod
    # def sfn_policy_statement() -> aws_iam.PolicyStatement:
    #     policy_statement = aws_iam.PolicyStatement()
    #     policy_statement.add_actions('states:SendTaskSuccess')
    #     policy_statement.add_actions('states:SendTaskFailure')
    #     policy_statement.add_actions('states:SendTaskHeartbeat')
    #     policy_statement.add_all_resources()
    #     policy_statement.effect = aws_iam.Effect.ALLOW
    #     policy_statement.sid = 'SfnHandsOn'
    #     return policy_statement

    def lambda_powertools(self):
        power_tools_layer = aws_sam.CfnApplication(
            scope=self,
            id='AWSLambdaPowertoolsLayer',
            location={
                'applicationId': ('arn:aws:serverlessrepo:eu-west-1:057560766410'
                                  ':applications/aws-lambda-powertools-python-layer'),
                'semanticVersion': '2.6.0'
            }
        )
        power_tools_layer_arn = power_tools_layer.get_att('Outputs.LayerVersionArn').to_string()
        power_tools_layer_version = aws_lambda.LayerVersion.from_layer_version_arn(
                scope=self,
                id='AWSLambdaPowertoolsLayerVersion',
                layer_version_arn=power_tools_layer_arn)
        return power_tools_layer_version


# class JobCompletionDetectionFunctionConstructor(Construct):
#
#     def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
#         super().__init__(scope, id_)
#
#         self.function = self.create_function()
#
#     def create_function(self) -> aws_cdk.aws_lambda:
#         function = aws_lambda.Function(
#             self,
#             'JobCompletionDetectionFunctionConstructor',
#             function_name='job_completion_detection',
#             runtime=aws_lambda.Runtime.PYTHON_3_9,
#             handler='lambda_function.lambda_handler',
#             code=aws_lambda.Code.from_asset('constructors/step_functions_flow_2/'
#                                             'functions_of_statemachine/job_completion_detection'),
#             timeout=aws_cdk.Duration.seconds(amount=300),
#             tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
#             layers=[self.lambda_powertools()],  # for X-Ray SDK
#             environment={}
#         )
#
#         # self.statemachine.grant_start_execution(function)
#         # self.state_machine.grant_task_response(self.receive_callback_token_function)
#         return function
#
#     def lambda_powertools(self):
#         power_tools_layer = aws_sam.CfnApplication(
#             scope=self,
#             id='AWSLambdaPowertoolsLayer',
#             location={
#                 'applicationId': ('arn:aws:serverlessrepo:eu-west-1:057560766410'
#                                   ':applications/aws-lambda-powertools-python-layer'),
#                 'semanticVersion': '2.6.0'
#             }
#         )
#         power_tools_layer_arn = power_tools_layer.get_att('Outputs.LayerVersionArn').to_string()
#         power_tools_layer_version = aws_lambda.LayerVersion.from_layer_version_arn(
#                 scope=self,
#                 id='AWSLambdaPowertoolsLayerVersion',
#                 layer_version_arn=power_tools_layer_arn)
#         return power_tools_layer_version
