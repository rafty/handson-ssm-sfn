from aws_cdk import Stack
from constructs import Construct
from constructors.vpc import vpc
from constructors.vpc import ec2
from constructors.vpc import resource_group


class HandsonVpc(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------
        # VPC
        vpc_config = {
            'vpc_name': 'handson',
            'vpc_cidr': '10.12.0.0/16',
            'vpc_azs': 1,
            'vpc_nat_gateways': 1,  # Todo: 使用しない場合、０にする
            # 'vpc_nat_gateways': 0,  # Todo: 使用しない場合、０にする
        }

        vpc_ = vpc.VpcConstructors(self, 'VPC', **vpc_config)

        # --------------------------------------------------
        # EC2
        role_sg_config = {
            'vpc': vpc_.vpc,
            'role_name': 'ssm_handson',
            'sg_name': 'ssm_handson',
        }
        role_sg = ec2.RoleSecurityGroupConstructors(self, 'HandsonRoleSG', **role_sg_config)

        # Todo: Instanceを暫く使用しない場合, 以下をコメントアウトする
        #  ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        instance_1_config = {
            'vpc': vpc_.vpc,
            'instance_name': 'handson_1',
            'instance_role': role_sg.role,
            'sg': role_sg.sg,
        }
        ec2.Ec2Constructors(self, 'HandsonInstance1', **instance_1_config)

        instance_2_config = {
            'vpc': vpc_.vpc,
            'instance_name': 'handson_2',
            'instance_role': role_sg.role,
            'sg': role_sg.sg,
        }
        ec2.Ec2Constructors(self, 'HandsonInstance2', **instance_2_config)
        # Todo: Instanceを暫く使用しない場合, 以下をコメントアウトする
        #  ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑


        # --------------------------------------------------
        # Resource Group
        resource_group_config = {
            'resource_group_name': 'handson',
        }
        resource_group.ResourceGroupConstructors(self, 'ResourceGroup1', **resource_group_config)
