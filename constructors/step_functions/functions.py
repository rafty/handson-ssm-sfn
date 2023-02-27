import aws_cdk
from constructs import Construct
from aws_cdk import aws_lambda
from aws_cdk import aws_sam
from aws_cdk import aws_stepfunctions
from aws_cdk import aws_iam
from aws_cdk import aws_s3
from aws_cdk import Aws


class FunctionConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.statemachine: aws_stepfunctions.StateMachine = kwargs.get('statemachine')
        self.function = self.create_function()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'StartStepFunctionsFunction',
            function_name='start_stepfunctions',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('starter/start_step_functions'),
            timeout=aws_cdk.Duration.seconds(amount=300),
            tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
            layers=[self.lambda_powertools()],  # for X-Ray SDK
            environment={
                'STATEMACHINE_ARN_FOR_HANDSON': self.statemachine.state_machine_arn,
            }
        )

        self.statemachine.grant_start_execution(function)

        return function

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



