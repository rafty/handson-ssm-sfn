import aws_cdk
from constructs import Construct
from aws_cdk import aws_lambda
from aws_cdk import aws_sam
from aws_cdk import aws_iam
from aws_cdk import Aws


class AutomationActionFunctionConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.function = self.create_function()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'SSMAutomationActionFunction',
            function_name='ssm_action_get_instance_id',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('constructors/Automation2/action_functions/get_instance_id'),
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
