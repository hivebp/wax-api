#!/bin/bash
for ((i=0;i<$(nproc);i++)); do cpufreq-set -c $i -g performance; done

