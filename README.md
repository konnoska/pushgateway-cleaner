![Tests](https://github.com/konnoska/pushgateway-cleaner/actions/workflows/tests.yaml/badge.svg?branch=main)

# Pushgateway-Cleaner

This is a lightweight app that cleans old data from prometheus [pushgateway](https://github.com/prometheus/pushgateway). You simple define the expiration duration and the pushgateway-cleaner takes care of the rest. Pushgateway-cleaner looks for metric groups that were last updated more that `CLEANER_EXPIRATION_DURATION` ago and deletes them.

## Note
If you require this tool 99.9% prometheus-pushgateway is not used as expected, **but** unfort in practice there are those 0.1% of the cases that the cost/effort of fixing this just doesn't worth it. This 0.1% is the reason this tool exists.

## Docker
```
docker pull konnoska/pushgateway-cleaner:latest
```

## Configuration
Pushgateway-cleaner is configured entirely through environmetn variables.

| Variable                    | Default        | Description | 
| ----------------------------| ---------------|-------------|
| CLEANER_EXPIRATION_DURATION | 24h            | Metric groups whose last push timestamp is older that this value are deleted. Accepted format {hours}h{Minutes}m{Seconds}s i.e. 1h30m20s, 1h, 10m |
| CLEANER_CLEANING_INTERVAL   | 12h            | Defines how often to start the cleaning routine.| 
| CLEANER_ENDPOINT            | localhost:9091 | Prometheus' pushgateway endpoint. |
| CLEANER_LOG_LVL             | INFO           | One of DEBUG, INFO, ERROR, WARNING. |
| CLEANER_DRY_RUN             |"FALSE"         |Set to "TRUE" to dry-run and see which metric groups would be deleted.|

## Proposed Deployment

If you run prometheus-pushgateway in k8s, we propose using the cleaner as a sidecar. The [community's helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-pushgateway) has builtin support for sidecars, so adding the following configuration to pushgateway's chart should be enough.
```
extraContainers: 
  - name: pushgateway-cleaner
    image: konnoska/pushgateway-cleaner:v1.0.0
    env:
    - name: CLEANER_EXPIRATION_DURATION
      value: "10m"
```
