from aws_cdk import Stack
from constructs import Construct
from constructors.automation import ssm
from constructors.automation import functions
from constructors.automation import automation_action_functions


class AutomationRunBookStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------
        # AWS SSM Automation Document

        automation_run_book = ssm.SsmConstructors(self, 'AutomationRunBook')
        book_name = automation_run_book.book_name

        # --------------------------------------------------
        # AWS Lambda function

        prop = {
            'automation_run_book_name': book_name
        }
        ssm_automation_function = functions.FunctionConstructors(self,
                                                                 'SsmAutomationConstructor',
                                                                 **prop)

        # --------------------------------------------------
        # SSM Automation Action - Lambda function

        automation_action_functions.AutomationActionFunctionConstructors(
            self,
            'SsmAutomationActionLambdaFunctionConstructor')

