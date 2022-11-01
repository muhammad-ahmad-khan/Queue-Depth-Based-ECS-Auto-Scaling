# Create target tracking policy using custom metric

Use aws cli to create target tracking policy using custom metric

## Dependencies

* aws cli

### How to execute the solution?

* Run following commands:

```
aws application-autoscaling register-scalable-target \
--service-namespace ecs \
--scalable-dimension ecs:service:DesiredCount \
--resource-id service/dev-worker-cluster/dev-worker-service \
--min-capacity 1 \
--max-capacity 10 \
--profile dev

aws application-autoscaling put-scaling-policy \
--policy-name ecs-scaling-based-on-message-consumption-rate \
--service-namespace ecs \
--resource-id service/dev-worker-cluster/dev-worker-service \
--scalable-dimension ecs:service:DesiredCount \
--policy-type TargetTrackingScaling \
--target-tracking-scaling-policy-configuration file://config-dev.json \
--profile dev

```


