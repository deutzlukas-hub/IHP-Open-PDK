#!/usr/bin/env python3
"""
Run inverter chain benchmarks for different chain sizes.

Runs make targets for both generic and tailored models with configurable repeats.
"""

import sys
from pathlib import Path

from benchmark import parse_args, run_benchmark

def main():
    """Run benchmarks for different inverter chain sizes."""

    args = parse_args()

    # Benchmark directory
    benchmark_dir = Path(__file__).parent

    # Run generic model
    generic_target = f"bench-tb_moslv_rf_c6288_tt_generic"
    run_benchmark(generic_target, args.j, args.REPEATS, benchmark_dir)

    # Run tailored model
    tailored_target = f"bench-tb_moslv_rf_c6288_tt_tailored"
    run_benchmark(tailored_target, args.j, args.REPEATS, benchmark_dir)


if __name__ == "__main__":
    sys.exit(main())
