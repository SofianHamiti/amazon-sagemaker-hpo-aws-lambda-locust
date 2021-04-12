import time
import boto3


class ApiGateway:
    def __init__(self, name, function_arn, role, region):
        self.name = name
        self.function_arn = function_arn
        self.role = role
        self.region = region
        self.create_response = None
        self.api_endpoint = None

        self.apigw_client = boto3.client('apigatewayv2', region_name=self.region)
        self.create_api()

    def create_api(self):
        try:
            self.create_response = self.apigw_client.create_api(
                Name=self.name,
                CredentialsArn=self.role,
                Target=self.function_arn,
                ProtocolType='HTTP',
                CorsConfiguration={
                    'AllowHeaders': ['Authorization'],
                    'AllowMethods': ['POST'],
                    'AllowOrigins': ['*'],
                    'MaxAge': 864000
                }
            )
            self.api_endpoint = self.create_response['ApiEndpoint']
            time.sleep(5)
        except Exception as e:
            raise e

    def delete_api(self):
        self.apigw_client.delete_api(
            ApiId=self.create_response['ApiId']
        )
