from constructs import Construct
from aws_cdk import aws_ec2


class VpcConstructors(Construct):

    def __init__(self, scope: "Construct", id_: str, **kwargs: dict) -> None:
        super().__init__(scope, id_)

        self.vpc_name = kwargs.get('vpc_name', None)

        self.vpc_cidr = kwargs.get('vpc_cidr', None)

        self.vpc_azs = kwargs.get('vpc_azs', None)
        self.vpc_nat_gateways = kwargs.get('vpc_nat_gateways', None)

        self.vpc = self.create_vpc()

    def create_vpc(self) -> aws_ec2.Vpc:

        vpc = aws_ec2.Vpc(
            self,
            'Vpc',
            vpc_name=self.vpc_name,

            ip_addresses=aws_ec2.IpAddresses.cidr(self.vpc_cidr),

            max_azs=self.vpc_azs,
            nat_gateways=self.vpc_nat_gateways,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name="Front",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    map_public_ip_on_launch=False,  # Todo: change for JIBUNDEMANABURABO
                    cidr_mask=24),
                aws_ec2.SubnetConfiguration(
                    name="Application",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24),
            ]
        )
        return vpc

