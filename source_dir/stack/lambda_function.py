import boto3


class LambdaFunction:
    def __init__(self, name, container, model_s3_uri, memory, role, region):
        self.name = name
        self.container = container
        self.model_s3_uri = model_s3_uri
        self.memory = memory
        self.role = role
        self.region = region
        self.create_response = None
        self.function_arn = None

        self.lambda_client = boto3.client('lambda', region_name=self.region)
        self.create_function()

    def create_function(self):
        self.create_response = self.lambda_client.create_function(
            Code={'ImageUri': self.container},
            FunctionName=self.name,
            Role=self.role,
            Environment={
                'Variables': {
                    'MODEL_S3_URI': self.model_s3_uri
                }
            },
            MemorySize=self.memory,
            Timeout=60,
            PackageType='Image'
        )
        self.function_arn = self.create_response['FunctionArn']
        creation_waiter = self.lambda_client.get_waiter('function_active')

        # wait the function is created
        try:
            creation_waiter.wait(FunctionName=self.name)
        except Exception as e:
            raise e

    def delete_function(self):
        self.lambda_client.delete_function(
            FunctionName=self.name
        )
