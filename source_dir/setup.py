from setuptools import setup, find_packages

setup(name='sagemaker-hpo-lambda-example',
      version='1.0',
      description='SageMaker HPO example for Lambda.',
      author='sofian',
      author_email='hamitis@amazon.com',
      packages=find_packages(exclude=('tests', 'docs')))