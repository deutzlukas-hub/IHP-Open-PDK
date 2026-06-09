#!/bin/bash

cd "$(dirname "$0")/build"

for test in *.sp; do
    echo "Running $test..."
    ngspice -b "$test"
done
