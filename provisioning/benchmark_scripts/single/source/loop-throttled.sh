declare -a targets=${targets:-\
( 500 1000 1500 2000 2500 3000 3500 4000 4500 5000 5500 6000 6500 7000 7500 8000 )}

echo "throughput targets (ops/s): ${targets[@]}"

for i in ${targets[@]}; do
    for w in ${workloads[@]}; do
        ansible-playbook "$basedir/benchmark-run.yaml" \
            -e "replicas=1" \
            -e "workload=$w" \
            -e "operation_count=$operation_count" \
            -e "threads=$threads" \
            -e "target=$i" \
            -e "gather_dest=$HOME/results/single/throttled/$i"
    done
done
