import aws_cdk
from constructs import Construct
from aws_cdk import aws_ec2
from aws_cdk import aws_iam


class VpcConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.vpc_name = kwargs.get('vpc_name', None)

        self.vpc_cidr = kwargs.get('vpc_cidr', None)
        # self.ip_addresses = aws_ec2.IpAddresses.cidr(kwargs.get('vpc_cidr', None))

        self.vpc_azs = kwargs.get('vpc_azs', None)
        self.vpc_nat_gateways = kwargs.get('vpc_nat_gateways', None)

        self.vpc = self.create_vpc()
        # self.create_ec2_instance()

    def create_vpc(self) -> aws_ec2.Vpc:

        vpc = aws_ec2.Vpc(
            self,
            'Vpc',
            vpc_name=self.vpc_name,

            # cidr=self.vpc_cidr,
            # ip_addresses=self.ip_addresses,
            ip_addresses=aws_ec2.IpAddresses.cidr(self.vpc_cidr),

            max_azs=self.vpc_azs,
            nat_gateways=self.vpc_nat_gateways,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name="Front",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    cidr_mask=24),
                aws_ec2.SubnetConfiguration(
                    name="Application",

                    # subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT,
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,

                    cidr_mask=24),
                # aws_ec2.SubnetConfiguration(
                #     name="DataStore",
                #     subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED,
                #     cidr_mask=24),
            ]
        )
        return vpc

    # def create_ec2_instance(self):
    #     _instance_type = aws_ec2.InstanceType('t3.micro')
    #     _subnet = aws_ec2.SubnetSelection(
    #         subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT
    #     )
    #     _ami = aws_ec2.AmazonLinuxImage(
    #         generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
    #     )
    #     _instance = aws_ec2.Instance(
    #         self,
    #         'TestInstance',
    #         instance_name='TestInstanceForSsmRunCommand',
    #         vpc=self.vpc,
    #         instance_type=_instance_type,
    #         vpc_subnets=_subnet,
    #         security_group=self.create_security_group(),
    #         role=self.create_iam_role(),
    #         machine_image=_ami
    #     )
    #
    # def create_iam_role(self):
    #     _role = aws_iam.Role(
    #         self,
    #         'SsmRunCommandTest',
    #         description='handson-ssm-runcommand',
    #         assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
    #         managed_policies=[
    #             aws_iam.ManagedPolicy.from_aws_managed_policy_name(
    #                 'AmazonSSMManagedInstanceCore'),
    #             aws_iam.ManagedPolicy.from_aws_managed_policy_name(
    #                 'CloudWatchAgentServerPolicy'
    #             )
    #         ]
    #     )
    #     return _role
    #
    # def create_security_group(self):
    #     _sg = aws_ec2.SecurityGroup(
    #         self,
    #         'SecurityGroup',
    #         security_group_name='handson_sg',
    #         vpc=self.vpc,
    #         allow_all_outbound=True
    #     )
    #     _sg.add_ingress_rule(
    #         peer=aws_ec2.Peer.any_ipv4(),
    #         connection=aws_ec2.Port.tcp(80)
    #     )
    #     _sg.add_ingress_rule(
    #         peer=aws_ec2.Peer.any_ipv4(),
    #         connection=aws_ec2.Port.tcp(443)
    #     )
    #     return _sg
    #

