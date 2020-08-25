from aws_cdk import core
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3_deployment as s3_deploy


# script used to initialize the EC2 instance when it is created
# note the S3 bucket name is parameterized
EC2_INIT_SCRIPT = \
"""#!/bin/bash
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ START ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# install packages
yum update -y
amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
yum install -y httpd mariadb-server php-mbstring
yum install -y php

# create a PHP info page
echo '<?php echo phpinfo(); ?>' > /var/www/html/info.php

# start web server
systemctl start httpd
systemctl enable httpd
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;

# start DB
systemctl start mariadb
systemctl enable mariadb

# loads the web application sources from the S3 bucket
echo "%(SOURCE_BUCKET_NAME)s" > /home/ec2-user/bucket_name.txt
mkdir /home/ec2-user/app
aws s3 sync "s3://%(SOURCE_BUCKET_NAME)s/" /home/ec2-user/app

# make web application files available to the web server
cd /home/ec2-user/app/
cp webapp/* /var/www/html/ -R

# initialize the DB
mysql < db/init.sql

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
"""


class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, ssh_key_name: str, **kw) -> None:
        super().__init__(scope, id, **kw)

        # start the web server (EC2 instance) in the default VPC
        vpc = ec2.Vpc.from_lookup(self, 'default_vpc', is_default=True)

        # create a security group for the web server that allows HTTP and SSH traffic
        sg = ec2.SecurityGroup(self,
                               'we_server_security_group',
                               vpc=vpc,
                               description='Allow HTTP ans SSH access',
                               allow_all_outbound=True)
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), 'SSH')
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'HTTP')
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), 'HTTPS')

        # create a bucket with all the web app components so they can be laoded into the
        # EC2 server later
        app_contents_bucket = s3.Bucket(self,
                                        'cdk_lamp_server',
                                        public_read_access=True,
                                        removal_policy=core.RemovalPolicy.DESTROY)
        s3_deploy.BucketDeployment(self,
                                   'deploy_webapp',
                                   sources=[s3_deploy.Source.asset('./web_app_contents')],
                                   destination_bucket=app_contents_bucket)

        # create an EC2 instance to work as a web server
        init_script = EC2_INIT_SCRIPT % dict(SOURCE_BUCKET_NAME=app_contents_bucket.bucket_name)
        web_server = ec2.Instance(self,
                                  'web_server',
                                  instance_name='cdk_web_app',
                                  instance_type=ec2.InstanceType('t2.micro'),
                                  machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
                                  vpc=vpc,
                                  vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                  security_group=sg,
                                  user_data=ec2.UserData.custom(init_script),
                                  key_name=ssh_key_name)

        # grant access to the EC2 instance
        app_contents_bucket.grant_read(web_server)

        # show the web_server public address as an output
        core.CfnOutput(self,
            'web-server-address',
            description='Web server public address',
            value=web_server.instance_public_dns_name
        )
