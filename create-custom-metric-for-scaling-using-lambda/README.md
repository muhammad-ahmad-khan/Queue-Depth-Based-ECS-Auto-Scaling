# Lambda Deployment for custom metric

lambda deployment for creating and maintaining data points of custom metric

## Dependencies

* sam cli
* aws cli

### How to execute the solution?

* Run following command:

```
sam deploy --stack-name create-custom-metric --template-file template.yml --s3-bucket test-deployment-bucket --capabilities CAPABILITY_IAM --region us-east-1 --parameter-overrides $(cat .sam-params-dev)

```