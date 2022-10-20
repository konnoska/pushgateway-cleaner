docker compose build
docker compose up -d

sleep 5
echo "some_metric 3.14" | curl --data-binary @- http://localhost:9091/metrics/job/some_job
PUSHED_VALUE=$(curl -s  http://localhost:9091/api/v1/metrics | yq ".data[0].some_metric.metrics[0].value")

if [ "$PUSHED_VALUE" = "3.14" ]; then
    echo "PUSH SUCCESS"
else
    echo "PUSH FAILED"
    exit 1
fi

echo "WAITING FOR DATA EXPIRATION AND CLEANUP..."
sleep 21

DATA=$(curl -s  http://localhost:9091/api/v1/metrics | yq ".data")


if [ "$DATA" = "[]" ]; then
    echo "DATA CLEARED SUCCESSFULLY"
else
    echo "DATA NOT CLEARED SUCCESSFULLY"
    echo "$DATA"
    exit 1
fi


docker compose down


