import aws_cdk
from constructs import Construct
from aws_cdk import aws_ec2
from aws_cdk import aws_iam
from aws_cdk import Tags
from aws_cdk import aws_resourcegroups


class ResourceGroupConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.resource_group_name = kwargs.get('resource_group_name', None)
        self.create_resource_group()

    def create_resource_group(self):
        resource_query = aws_resourcegroups.CfnGroup.ResourceQueryProperty(
            query=aws_resourcegroups.CfnGroup.QueryProperty(
                tag_filters=[
                    aws_resourcegroups.CfnGroup.TagFilterProperty(key='env', values=['handson'])]),
            type='TAG_FILTERS_1_0'
        )

        cfn_group = aws_resourcegroups.CfnGroup(self,
                                                'HandsonResourceGroup',
                                                name=self.resource_group_name,
                                                resource_query=resource_query)

        aws_cdk.CfnOutput(
            self,
            'HandsonResourceGroupOutput',
            value=self.resource_group_name,
            description='Handson instance resource group',
            export_name='HandsonResourceGroupName'
        )
