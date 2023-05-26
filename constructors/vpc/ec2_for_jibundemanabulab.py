from constructs import Construct
from aws_cdk import aws_ec2
from aws_cdk import aws_iam
from aws_cdk import Tags


class RoleSecurityGroupConstructors(Construct):
    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.vpc: aws_ec2.Vpc = kwargs.get('vpc', None)
        self.role_name = kwargs.get('role_name', None)
        self.sg_name = kwargs.get('sg_name', None)

        self.role = self.create_iam_role()
        self.sg = self.create_security_group()

    def create_iam_role(self):
        _role = aws_iam.Role(
            self,
            f'Role{self.role_name}',
            description='handson-ssm-runcommand',
            assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchAgentServerPolicy')
            ]
        )
        return _role

    def create_security_group(self):
        _sg = aws_ec2.SecurityGroup(
            self,
            f'SG{self.role_name}',
            security_group_name=self.sg_name,
            vpc=self.vpc,
            allow_all_outbound=True
        )
        _sg.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.tcp(80)
        )
        _sg.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.tcp(443)
        )
        return _sg


class Ec2Constructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.vpc: aws_ec2.Vpc = kwargs.get('vpc', None)
        self.instance_name = kwargs.get('instance_name', None)
        self.instance_role = kwargs.get('instance_role', None)
        self.sg = kwargs.get('sg', None)
        self.instance = self.create_ec2_instance()

        # Tag & Resource Group
        self.tag_to_instance('env', 'handson')
        self.tag_to_instance('InstanceName', self.instance_name)

    # def create_ec2_instance(self) -> aws_ec2.Instance:
    #     _instance_type = aws_ec2.InstanceType('t3.micro')
    #
    #     _subnets = aws_ec2.SubnetSelection(
    #         subnets=self.vpc.select_subnets(
    #             subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS
    #         ).subnets
    #     )
    #
    #     _ami = aws_ec2.AmazonLinuxImage(
    #         generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
    #     )
    #     _instance = aws_ec2.Instance(
    #         self,
    #         f'id_{self.instance_name}',
    #         instance_name=self.instance_name,
    #         vpc=self.vpc,
    #         instance_type=_instance_type,
    #         vpc_subnets=_subnets,
    #         security_group=self.sg,
    #         role=self.instance_role,
    #         machine_image=_ami
    #     )
    #     return _instance

    # Todo:
    #  associatePublicIpAddressをfalseにするためには、network_interfacesで指定しなければならない。
    #  network_interfacesは、aws_ec2.Instance()では使用できず、CfnInstance()を使用する。

    def create_ec2_instance(self) -> aws_ec2.Instance:
        _instance_type = aws_ec2.InstanceType('t3.micro')
        _instance_profile = aws_iam.CfnInstanceProfile(
            self,
            f'{self.instance_name}InstanceProfile',
            roles=[self.instance_role.role_name]
        )
        _ami = aws_ec2.AmazonLinuxImage(
            generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        )

        _instance = aws_ec2.CfnInstance(
            self,
            f'id_{self.instance_name}',
            tags=[{
                'key': 'Name',
                'value': self.instance_name,
            }],
            instance_type=_instance_type,
            iam_instance_profile=_instance_profile.instance_profile_name,
            network_interfaces=[{
                'deviceIndex': '0',
                'associatePublicIpAddress': False,
                'subnetId': self.vpc.public_subnets[0].subnet_id,
                'groupSet': [self.sg.security_group_id]

            }],
            image_id=_ami,
        )
        return _instance

    def tag_to_instance(self, key: str, value: str):
        Tags.of(self.instance).add(key, value)
