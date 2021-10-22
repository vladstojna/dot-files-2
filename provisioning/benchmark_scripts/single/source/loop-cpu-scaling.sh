# No CPU limit (0.00) must be first in loop because updating a
# container with --cpus=0.00 does not update the NanoCPUs value

declare -A cpu_props=${cpu_props:-\
( [0.20]=4 [0.30]=4 [0.40]=4 [0.50]=4 [0.60]=4 [0.70]=4 [0.80]=4 [0.90]=4 [1.00]=4 )}

echo "CPU limits (%): ${!cpu_props[@]}"
echo "Threads: ${cpu_props[@]}"

for i in ${!cpu_props[@]}; do
    ansible-playbook "$basedir/server-single-update.yaml" \
        -e "{ \"resources\": { \"single\": { \"limit\": { \"cpu\": $i } } } }"
    for w in ${workloads[@]}; do
        ansible-playbook "$basedir/benchmark-run.yaml" \
            -e "replicas=1" \
            -e "workload=$w" \
            -e "operation_count=$operation_count" \
            -e "threads=${cpu_props[$i]}" \
            -e "target=0" \
            -e "gather_dest=$HOME/results/single/cpu/$i"
    done
done
