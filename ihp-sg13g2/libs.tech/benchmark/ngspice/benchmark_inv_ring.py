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

    # Configuration
    num_invs = [11, 21, 51, 101]

    # Benchmark directory
    benchmark_dir = Path(__file__).parent

    for num_inv in num_invs:

        # Run generic model
        generic_target = f"bench-tb_moslv_rf_inv_ring_N{num_inv}_tt_generic"
        run_benchmark(generic_target, args.j, args.REPEATS, benchmark_dir)

        # Run tailored model
        tailored_target = f"bench-tb_moslv_rf_inv_ring_N{num_inv}_tt_tailored"
        run_benchmark(tailored_target, args.j, args.REPEATS, benchmark_dir)


if __name__ == "__main__":
    sys.exit(main())
