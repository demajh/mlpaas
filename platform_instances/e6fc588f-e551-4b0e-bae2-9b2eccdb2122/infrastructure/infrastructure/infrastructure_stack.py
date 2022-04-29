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
        lambda_function_name = "extract_load-d61aea8a-7962-463e-b02d-8171bbd0654f"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = "/home/ubuntu/mlpaas/platform_instances/e6fc588f-e551-4b0e-bae2-9b2eccdb2122/services/29217f46-cfc6-4c35-b40d-e76b0d409807")
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
            



        

        

        

