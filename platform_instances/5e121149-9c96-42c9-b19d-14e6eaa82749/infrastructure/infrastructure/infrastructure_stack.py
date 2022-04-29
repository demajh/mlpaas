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
        lambda_function_name = "extract_load-cead2776-46db-45c0-a95b-e5c436406163"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = "/home/ubuntu/mlpaas/platform_instances/5e121149-9c96-42c9-b19d-14e6eaa82749/services/cf66d9fa-954d-4fb3-9911-8c9728e2b56b")
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
            



        

        

        

