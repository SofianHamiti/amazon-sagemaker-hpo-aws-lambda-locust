import os
import json
import logging
import argparse
import invokust
from load_test.api_user import ApiUser
from stack.api_gateway import ApiGateway
from stack.lambda_function import LambdaFunction

logging.basicConfig(level=logging.INFO)


def run_load_test(host):
    settings = invokust.create_settings(
        classes=[ApiUser],
        host=host,
        num_users=1000,
        spawn_rate=100,
        run_time='1m'
    )
    loadtest = invokust.LocustLoadTest(settings)
    loadtest.run()
    return loadtest.stats()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--container", type=str)
    parser.add_argument("--model_s3_uri", type=str)
    parser.add_argument("--role", type=str)
    parser.add_argument("--region", type=str)
    parser.add_argument("--lambda_memory", type=int)
    args, _ = parser.parse_known_args()

    # ==================================================
    # ================= CREATE STACK ===================
    # ==================================================
    logging.info('CREATING LAMBDA FUNCTION')
    # get name for lambda and api gateway from SageMaker job name
    training_env = json.loads(os.environ['SM_TRAINING_ENV'])
    name = training_env['job_name']
    
    lambda_function = LambdaFunction(
        name=name,
        container=args.container,
        memory=int(args.lambda_memory),
        model_s3_uri=args.model_s3_uri,
        role=args.role,
        region=args.region
    )

    logging.info('CREATING API')
    api = ApiGateway(
        name=name,
        function_arn=lambda_function.function_arn,
        role=args.role,
        region=args.region
    )
    # ==================================================
    # ================= LOAD TEST API ==================
    # ==================================================
    try:
        logging.info('LOAD TESTING THE API')
        stats = run_load_test(host=api.api_endpoint)
        
        # get response time percentiles
        response_time_percentile = stats['requests']['POST_/']['response_time_percentiles'][95]
        logging.info(f'REPONSE TIME PERCENTILES: {response_time_percentile}')
        logging.info(f'LAMBDA MEMORY: {args.lambda_memory}')
        
        # we create this aggregate score to optimize both latency and lambda memory allocation (cost)
        aggregate_score = int(args.lambda_memory) * response_time_percentile
        logging.info(f'AGGREGATE SCORE: {aggregate_score}')

    except Exception as e:
        logging.error(e)

        # ==================================================
        # ================ DELETE STACK ====================
        # ==================================================
    
    finally:
        logging.info('DELETING LAMBDA FUNCTION')
        api.delete_api()
        logging.info('DELETING API')
        lambda_function.delete_function()
