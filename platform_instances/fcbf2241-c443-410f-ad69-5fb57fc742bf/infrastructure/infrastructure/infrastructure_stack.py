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
        lambda_function_name = "extract_load-872c5b39-ab45-4f0e-82bb-4685566d02a5"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = "/home/ubuntu/mlpaas/platform_instances/fcbf2241-c443-410f-ad69-5fb57fc742bf/services/a666b3e7-0b4c-4bf6-a20f-1f506dd21af7")
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
            



        

        

        

