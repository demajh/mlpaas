import time
import json
import boto3
from aws_cdk import (Duration,
                     Stack,
                     CfnOutput,
                     aws_iam as _iam,
                     aws_ecs_patterns as _ecs_patterns,
                     aws_ec2 as _ec2,
                     aws_lambda as _lambda,
                     aws_autoscaling as _autoscaling,
                     aws_ecs as _ecs)
from constructs import Construct

class DBTClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        config_path = "s3://magnify-data-pipeline/configs/config.json"
        config, cluster, cluster_name, step_role = self.initialize_pipeline_resources(config_path)
        broker_name = self.create_broker(config, step_role)

        return
    
    def initialize_pipeline_resources(self, config_fname):

        config = self.load_config(config_fname)

        step_role_name = config["role_name"]
        step_role_arn = config["role_arn"]
        step_role = _iam.Role.from_role_arn(self, step_role_name, step_role_arn, mutable=False)

        cluster_name = config["cluster_name"]#config["service_name"] + "-cluster-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
        vpc = _ec2.Vpc.from_lookup(self, config["vpc_name"], is_default=True)
        cluster = _ecs.Cluster(self, config["cluster_name"], cluster_name=cluster_name, vpc=vpc)
        print(dir(cluster))
        auto_scaling_group = _autoscaling.AutoScalingGroup(self, config["autoscaling_group_name"],
                                                          vpc=vpc,
                                                          instance_type=_ec2.InstanceType(config["instance_type"]),
                                                          block_devices=[_autoscaling.BlockDevice(device_name="/dev/xvda", volume=_autoscaling.BlockDeviceVolume.ebs(500))],
                                                          machine_image=_ecs.EcsOptimizedImage.amazon_linux2(hardware_type=_ecs.AmiHardwareType("GPU")),
                                                          desired_capacity=1)
        auto_scaling_group.add_to_role_policy(_iam.PolicyStatement(actions=["ecr:GetAuthorizationToken", "ecr:BatchGetImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:PutImage"], resources=["*"]))
        capacity_provider = _ecs.AsgCapacityProvider(self, "AsgCapacityProvider",
                                                    auto_scaling_group=auto_scaling_group
        )
        cluster.add_asg_capacity_provider(capacity_provider)
        
        return config, cluster, cluster_name, step_role

    def create_lambda(self, imagedir, step_role):

        lambda_function_name = "ml_data_pipeline_broker"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = imagedir)
        # create lambda function
        function = _lambda.Function(self, lambda_function_name,
                                    function_name=lambda_function_name,
                                    runtime=_lambda.Runtime.FROM_IMAGE,
                                    handler=_lambda.Handler.FROM_IMAGE,
                                    code=curr_image,
                                    role=step_role,
                                    memory_size=10000,
                                    timeout=Duration.seconds(900),
                                    environment=dict(PYTHONPATH='/'))

        return lambda_function_name

    def create_broker(self, config, broker_role):

        imagedir = "steps/broker"
        function_name = self.create_lambda(imagedir, broker_role)
        
        return function_name
    
    def load_config(self, config_path):

        if "s3" in config_path:
            config = self.download_config_s3(config_path)
        elif os.path.exists(config_path):
            config = json.load(open(config_path, "r"))
        else:
            raise Exception("Config path type not recognized.")

        return config
    
    def download_config_s3(self, s3_path):

        bucket = s3_path.split("/")[2]
        key = "/".join(s3_path.split("/")[3:])
        s3 = boto3.resource('s3')
        content_object = s3.Object(bucket, key)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)

        return json_content    
