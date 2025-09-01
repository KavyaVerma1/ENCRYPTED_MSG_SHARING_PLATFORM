import boto3

REGION = 'eu-north-1' 
VPC_CIDR = '10.0.0.0/16'
PUBLIC_SUBNET_CIDR = '10.0.1.0/24'
PRIVATE_SUBNET_CIDR = '10.0.2.0/24'
AMI_ID = 'ami-0c4fc5dcabc9df21d' 
INSTANCE_TYPE = 't3.micro'
KEY_PAIR_NAME = 'msg_sharing_p' 
DB_ENGINE = 'RDS' 
DB_NAME = 'encryptedmessagesdb'
DB_USER = 'admin'
DB_PASSWORD = 'kavya123' 
DB_INSTANCE_CLASS = 'db.t2.micro'
DB_ALLOCATED_STORAGE = 20

ec2= boto3.client('ec2', region_name=REGION)
rds_client = boto3.client('rds', region_name=REGION)

def create_vpc_resources():
    vpc = ec2.create_vpc(CidrBlock=VPC_CIDR)
    igw = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)

    public_subnet = vpc.create_subnet(
        CidrBlock=PUBLIC_SUBNET_CIDR,
        AvailabilityZone=f'{REGION}a'
    )
    private_subnet = vpc.create_subnet(
        CidrBlock=PRIVATE_SUBNET_CIDR,
        AvailabilityZone=f'{REGION}b'
    )
    private_subnet.create_tags(Tags=[{'Key': 'Name', 'Value': 'AppPrivateSubnet'}])
    print(f"Private Subnet created")

    public_route_table = vpc.create_route_table()
    public_route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
    public_route_table.associate_with_subnet(SubnetId=public_subnet.id)
    private_route_table = vpc.create_route_table()
    private_route_table.associate_with_subnet(SubnetId=private_subnet.id)
    nacl = ec2.create_network_acl(VpcId=vpc.id)
    ec2.create_network_acl_entry(
        CidrBlock='0.0.0.0/0',
        NetworkAclId=nacl['NetworkAcl']['NetworkAclId'],
        PortRange={'From': 0, 'To': 65535},
        RuleAction='allow',
    )
    ec2.network_acl.associate_with_subnet(subnet_id=public_subnet.id)

    return vpc, public_subnet, private_subnet, igw

def create_security_groups(vpc_id):
    print("Creating EC2 security group...")
    ec2_sg = ec2.create_security_group(
        Description='Allow HTTP and HTTPS traffic',
        GroupName='WebTrafficSecurityGroup',
        VpcId=vpc_id
    )
    ec2_sg_id = ec2_sg['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=ec2_sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    return ec2_sg_id

def launch_ec2_instance():

    instance = ec2.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MaxCount=1,
        MinCount=1,
        KeyName=KEY_PAIR_NAME,
    )
    instance_id = instance[0].id
    return instance_id

def create_database():
    DB_ENGINE == 'RDS'
    rds_client.create_db_instance(
            DBName=DB_NAME,
            DBInstanceIdentifier='encrypted-messages-db',
            AllocatedStorage=DB_ALLOCATED_STORAGE,
            DBInstanceClass=DB_INSTANCE_CLASS,
            Engine='mysql',
        )

if __name__ == '__main__':
    vpc, public_subnet, private_subnet, igw=create_vpc_resources()
    ec2_sg_id=create_security_groups(vpc.id)
    instance_id = launch_ec2_instance()
    create_database()
