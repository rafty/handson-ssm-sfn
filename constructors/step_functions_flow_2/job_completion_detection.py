import aws_cdk
from constructs import Construct
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from aws_cdk import aws_sam
from aws_cdk import aws_logs
from aws_cdk import aws_logs_destinations
from aws_cdk import aws_dynamodb


class JobCompletionDetectionFunctionConstructor(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.callback_table: aws_dynamodb.Table = kwargs.get('callback_table')

        self.function = self.create_function()
        self.create_logs_subscription()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'JobCompletionDetectionFunctionConstructor',
            function_name='job_completion_detection',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('constructors/step_functions_flow_2/'
                                            'functions_of_statemachine/job_completion_detection'),
            timeout=aws_cdk.Duration.seconds(amount=300),
            tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
            layers=[self.lambda_powertools()],  # for X-Ray SDK
            environment={
                'CALLBACK_TABLE_NAME': self.callback_table.table_name
            }
        )

        self.callback_table.grant_read_write_data(function)
        function.add_to_role_policy(self.sfn_policy_statement())

        return function

    @staticmethod
    def sfn_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('states:SendTaskSuccess')
        policy_statement.add_actions('states:SendTaskFailure')
        policy_statement.add_actions('states:SendTaskHeartbeat')
        policy_statement.add_all_resources()
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.sid = 'SfnHandsOn'
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

    def create_logs_subscription(self):

        # Log Group
        """ - 既存のLogGroupを使用する場合"""
        log_group = aws_logs.LogGroup.from_log_group_name(
            self,
            'LogGroup',
            log_group_name='/aws/ssm/AWS-RunShellScript',)

        # Logs Subscription Filter
        """ 検知する文字列をany_term()に追加する。
          - 'Complete!' 
          - 'No packages marked for update'  
        """
        # Todo:
        #  RunCommandの成功のみを検知している。
        #  本来はリトライが必要なRunCommandのErrorも検知すること
        #  プロセスやInstanceの監視も行うこと
        aws_logs.SubscriptionFilter(
            self,
            'LambdaSubscriptionFilter',
            log_group=log_group,
            destination=aws_logs_destinations.LambdaDestination(self.function),
            filter_pattern=aws_logs.FilterPattern.any_term('Complete!',
                                                           'No packages marked for update'),
        )
