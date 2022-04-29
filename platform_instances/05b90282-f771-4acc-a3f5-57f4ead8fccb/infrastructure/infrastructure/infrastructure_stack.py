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
        lambda_function_name = "extract_load-ce79ee13-f130-4106-898f-abc75b7f686a"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = "/home/ubuntu/mlpaas/platform_instances/05b90282-f771-4acc-a3f5-57f4ead8fccb/services/1d1a04c0-a10a-46b9-afa9-37a95aeac3ae")
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
            



        

        

        

