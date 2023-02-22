import aws_cdk
from constructs import Construct
from aws_cdk import aws_dynamodb


class CallbackTableConstructor(Construct):
    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)
        self.table_name = 'CallBackTable'
        self.partition_key = 'ssm_run_command_id'  # SSM Runcommand Command Id
        self.sort_key = 'instance_id'  # Instance Id

        self.table = self.create_callback_table()

    def create_callback_table(self) -> aws_dynamodb.Table:
        table = aws_dynamodb.Table(
            self,
            id='CallBackTable',
            table_name=self.table_name,
            partition_key=aws_dynamodb.Attribute(name=self.partition_key,
                                                 type=aws_dynamodb.AttributeType.STRING),
            sort_key=aws_dynamodb.Attribute(name=self.sort_key,
                                            type=aws_dynamodb.AttributeType.STRING),
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
        )
        return table
