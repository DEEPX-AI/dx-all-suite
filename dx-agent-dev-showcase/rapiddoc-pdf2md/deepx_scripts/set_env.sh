#!/bin/bash
# Usage: source ./deepx_scripts/set_env.sh [CUSTOM_INTER_OP_THREADS_COUNT] [CUSTOM_INTRA_OP_THREADS_COUNT] [DXRT_DYNAMIC_CPU_THREAD] [DXRT_TASK_MAX_LOAD] [NFH_INPUT_WORKER_THREADS] [NFH_OUTPUT_WORKER_THREADS]
# Example: source ./deepx_scripts/set_env.sh 1 2 3 4 5 6
# Use -1 to unset a specific variable: source ./deepx_scripts/set_env.sh 1 -1 3 4 5 6
if [ "$1" = "-1" ]; then
    unset CUSTOM_INTER_OP_THREADS_COUNT
    echo "CUSTOM_INTER_OP_THREADS_COUNT unset"
elif [ -n "$1" ]; then
    export CUSTOM_INTER_OP_THREADS_COUNT=$1
    echo "CUSTOM_INTER_OP_THREADS_COUNT=$CUSTOM_INTER_OP_THREADS_COUNT"
fi
if [ "$2" = "-1" ]; then
    unset CUSTOM_INTRA_OP_THREADS_COUNT
    echo "CUSTOM_INTRA_OP_THREADS_COUNT unset"
elif [ -n "$2" ]; then
    export CUSTOM_INTRA_OP_THREADS_COUNT=$2
    echo "CUSTOM_INTRA_OP_THREADS_COUNT=$CUSTOM_INTRA_OP_THREADS_COUNT"
fi
if [ "$3" = "-1" ]; then
    unset DXRT_DYNAMIC_CPU_THREAD
    echo "DXRT_DYNAMIC_CPU_THREAD unset"
elif [ -n "$3" ]; then
    export DXRT_DYNAMIC_CPU_THREAD=$3
    echo "DXRT_DYNAMIC_CPU_THREAD=$DXRT_DYNAMIC_CPU_THREAD"
fi
if [ "$4" = "-1" ]; then
    unset DXRT_TASK_MAX_LOAD
    echo "DXRT_TASK_MAX_LOAD unset"
elif [ -n "$4" ]; then
    export DXRT_TASK_MAX_LOAD=$4
    echo "DXRT_TASK_MAX_LOAD=$DXRT_TASK_MAX_LOAD"
fi
if [ "$5" = "-1" ]; then
    unset NFH_INPUT_WORKER_THREADS
    echo "NFH_INPUT_WORKER_THREADS unset"
elif [ -n "$5" ]; then
    export NFH_INPUT_WORKER_THREADS=$5
    echo "NFH_INPUT_WORKER_THREADS=$NFH_INPUT_WORKER_THREADS"
fi
if [ "$6" = "-1" ]; then
    unset NFH_OUTPUT_WORKER_THREADS
    echo "NFH_OUTPUT_WORKER_THREADS unset"
elif [ -n "$6" ]; then
    export NFH_OUTPUT_WORKER_THREADS=$6
    echo "NFH_OUTPUT_WORKER_THREADS=$NFH_OUTPUT_WORKER_THREADS"
fi