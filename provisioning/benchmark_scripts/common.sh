basedir="$HOME/provisioning"
dirname="$(dirname "$0")"

declare -a workloads=${workloads:-( workloada workloadb workloadc workloadf )}
record_count=${record_count:-50000}
operation_count=${operation_count:-50000}
threads=${threads:-4}
deploy_pause=${deploy_pause:-10}

export ANSIBLE_CONFIG="$basedir/ansible.cfg"
export ANSIBLE_INVENTORY="$basedir/inventory.ini"

echo "basedir: $basedir"
echo "workloads: ${workloads[@]}"
echo "record_count: $record_count"
echo "operation_count: $operation_count"
echo "threads: $threads"
echo "deploy_pause: $deploy_pause"
echo "ANSIBLE_CONFIG: $ANSIBLE_CONFIG"
echo "ANSIBLE_INVENTORY: $ANSIBLE_INVENTORY"
