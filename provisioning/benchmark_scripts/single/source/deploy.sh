ansible-playbook "$basedir/server-single-deploy.yaml"

for i in $(seq "$deploy_pause"); do
    echo -n >&2 '.'
    sleep 1
done
echo

ansible-playbook "$basedir/benchmark-load.yaml" \
    -e workload=workloada \
    -e "record_count=$record_count" \
    -e show_output=1
