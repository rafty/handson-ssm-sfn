import aws_cdk
from constructs import Construct
from aws_cdk import aws_lambda
from aws_cdk import aws_sam
from aws_cdk import aws_iam
from aws_cdk import aws_s3
from aws_cdk import Aws


class FunctionConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.automation_run_book_name = kwargs.get('automation_run_book_name', None)
        self.output_bucket_name = f'ssm-automation-output-2-{Aws.ACCOUNT_ID}-{Aws.REGION}'
        self.function = self.create_function()

    def create_function(self) -> aws_cdk.aws_lambda:
        function = aws_lambda.Function(
            self,
            'SSMAutomationFunction',
            function_name='ssm_automation_function_2',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('handson_app/ssm_automation_2'),
            timeout=aws_cdk.Duration.seconds(amount=300),
            tracing=aws_lambda.Tracing.ACTIVE,  # for X-Ray
            layers=[self.lambda_powertools()],  # for X-Ray SDK
            environment={
                'OUTPUT_BUCKET_NAME': self.output_bucket_name,
                'AUTOMATION_DOCUMENT_NAME': self.automation_run_book_name,
                'ACCOUNT_ID': Aws.ACCOUNT_ID,
                'REGION': Aws.REGION,
                'TARGET_RESOURCE_GROUP_NAME': 'handson',
            }
        )

        function.add_to_role_policy(self.ssm_policy_statement())
        function.add_to_role_policy(self.tag_policy_statement())
        function.add_to_role_policy(self.iam_policy_statement())
        function.add_to_role_policy(self.ec2_policy_statement())

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/README.html#sharing-buckets-between-stacks
        output_bucket = self.s3_bucket_for_ssm_run_command_output()
        output_bucket.grant_read_write(function)

        return function

    @staticmethod
    def ssm_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('ssm:StartAutomationExecution')
        policy_statement.add_actions('ssm:GetAutomationExecution')
        policy_statement.add_actions('ssm:ListCommandInvocations')
        policy_statement.add_actions('ssm:SendCommand')
        policy_statement.add_actions('ssm:ListCommands')
        policy_statement.add_actions('ssm:DescribeInstanceInformation')
        policy_statement.add_actions('lambda:InvokeFunction')
        policy_statement.add_all_resources()
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.sid = 'SsmAutomationHandsOn2'
        return policy_statement

    @staticmethod
    def tag_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('tag:GetResources')
        policy_statement.add_actions('resource-groups:ListGroupResources')
        policy_statement.add_all_resources()
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.sid = 'SsmAutomationTagHandsOn2'
        return policy_statement

    @staticmethod
    def iam_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('iam:PassRole')
        # policy_statement.add_resources(
        #     f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/AWS-SystemsManager-AutomationAdministrationRole")
        policy_statement.add_resources(
            f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/AWS-SystemsManager-AutomationExecutionRole")
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.sid = 'IamPassRoleForSsmAutomationAssumeRole2'
        return policy_statement

    @staticmethod
    def ec2_policy_statement() -> aws_iam.PolicyStatement:
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions('ec2:DescribeInstances')
        policy_statement.add_all_resources()
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.sid = 'SsmAutomationAction'
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

    def s3_bucket_for_ssm_run_command_output(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/README.html#sharing-buckets-between-stacks

        output_bucket = aws_s3.Bucket(self,
                                      'S3BucketConstruct',
                                      bucket_name=self.output_bucket_name,
                                      removal_policy=aws_cdk.RemovalPolicy.DESTROY)

        aws_cdk.CfnOutput(
            self,
            'SsmAutomationOutputBucketName',
            value=output_bucket.bucket_name,
            description='SSM Automation Output bucket name',
            export_name='SsmAutomationOutputBucketName2'
        )

        return output_bucket
