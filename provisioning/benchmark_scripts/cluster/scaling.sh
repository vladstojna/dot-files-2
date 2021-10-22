#!/usr/bin/env bash

source "$(dirname "$0")/../common.sh"

max_shards=${max_shards:-1}
cpu_limit=${cpu_limit:-0.00}

echo "Maximum number of shards: $max_shards"
echo "Shard CPU % limit: $cpu_limit"

for count in $(seq $max_shards); do
    ansible-playbook "$basedir/node-update-labels.yaml" \
        -e "{\"count\": { \"coordinator\": 1, \"agency\": 1, \"dbserver\": $count } }"

    ansible-playbook "$basedir/server-cluster-all.yaml" \
        -e "constrained_placement=yes" \
        -e "dbserver_count=$count" \
        -e "coordinator_count=1" \
        -e "cleanup=yes" \
        -e "wait_sync=no" \
        -e "duration=$deploy_pause" \
        -e "{\"resources\": {\"dbserver\": {\"limit\": {\"cpu\": $cpu_limit } } } }"

    ansible-playbook "$basedir/benchmark-load.yaml" \
        -e "workload=workloada" \
        -e "record_count=$record_count" \
        -e "show_output=1"

    for w in ${workloads[@]}; do
        ansible-playbook "$basedir/benchmark-run.yaml" \
            -e "replicas=1" \
            -e "workload=$w" \
            -e "operation_count=$operation_count" \
            -e "threads=$threads" \
            -e "target=0" \
            -e "gather_dest=$HOME/results/cluster/shards/$cpu_limit/$count"
    done
done

ansible-playbook "$basedir/server-cluster-destroy.yaml"
