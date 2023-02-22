from aws_cdk import Stack
from constructs import Construct
from constructors.run_command import functions


class RunCommandStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------
        # AWS Lambda function
        self.run_command_function = functions.FunctionConstructors(self, 'RunCommandFunction')
