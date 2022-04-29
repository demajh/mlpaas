from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as _sqs,
    aws_lambda as _lambda,
    aws_iam as _iam,
)
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        role = _iam.Role.from_role_arn(self, "model-dev", "arn:aws:iam::545555405821:role/model-dev", mutable=False)
        lambda_function_name = "extract_load-d0a90877-a40c-4376-878e-249264bf1cf2"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = "/home/ubuntu/mlpaas/platform_instances/d98ab403-91c1-4365-986a-3d5e5ca9ed9e/services/bf8bab3c-1886-48a3-a064-caa05a292da0")
        # create lambda function
        function = _lambda.Function(self, lambda_function_name,
                                    function_name=lambda_function_name,
                                    runtime=_lambda.Runtime.FROM_IMAGE,
                                    handler=_lambda.Handler.FROM_IMAGE,
                                    code=curr_image,
                                    role=role,
                                    memory_size=10000,
                                    timeout=Duration.seconds(900),
                                    environment=dict(PYTHONPATH='/'))
            



        

        

        

