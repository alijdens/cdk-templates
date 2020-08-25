# CDK LAMP server

This CDK template creates a web server with an application running on LAMP. The stack consists of an S3 bucket where a web application is uploaded (see `web_app_contents`) and an EC2 instance that installs MariaDB and PHP7 when it is created. Finally, the instance pulls the web application from the S3 bucket.


## Deployment

In order to get SSH access into the EC2 instance (the web server), you need a *key-pair* to be associated with it. You can create key pairs through:

 * the AWS console under the EC2 dashboard. Note that when a new key pair is generated, the browser will prompt to save the newly created private key. You need to store it in your local computer and don't lose it because it cannot be recovered. When the key pair is created, you'll have to assign it a **name**.
 * using the `aws cli` tool:

```shell
aws ec2 create-key-pair --key-name <KEY_NAME>
```

You'll have to set an environment variable `SSH_KEY_NAME` (containing the key pair name) when deploying this infrastructure with CDK.


## SSH access

In order to access the web server, you'll have to use SSH with the private key obtained when the key pair was created. You can use the following `bash` command:

```shell
ssh -i <path/to/private/key.pem> ec2-user@<INSTANCE_PUBLIC_DNS>
```

You can obtain `<INSTANCE_PUBLIC_DNS>` from the EC2 dashboard in the AWS console or by looking at the `cdk deploy` output parameters:

```
[deployment steps]

Outputs:
server.webserveraddress = <INSTANCE_PUBLIC_DNS>
```

### Troubleshooting

 * https://stackoverflow.com/questions/9270734/ssh-permissions-are-too-open-error
 * *You need to be root to perform this command.*: `sudo` has no password.


## CDK help

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
