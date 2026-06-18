#!/usr/bin/env python3
"""
Run inverter chain benchmarks for different chain sizes.

Runs make targets for both generic and tailored models with configurable repeats.
"""

import subprocess
import sys
from pathlib import Path
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run inverter-chain benchmarks."
    )

    parser.add_argument(
        "--REPEATS",
        type=int,
        default=7,
        help="Number of benchmark repeats passed to make as REPEATS=<n>.",
    )

    parser.add_argument(
        "-j",
        type=int,
        default=1,
        help="Number of parallel jobs passed to make as -j<n>.",
    )

    return parser.parse_args()



def run_benchmark(
        target: str,
        repeats: int = 7,
        j: int = 1,
        cwd: Path = None,

    ) -> bool:


    subprocess.run(
        ["make", target, f"-j{j}", f"REPEATS={repeats}"],
        cwd=cwd,
        check=True,
        text=True
    )


def main():
    """Run benchmarks for different inverter chain sizes."""

    args = parse_args()

    # Configuration
    num_invs = [10, 20, 50, 100, 200, 500, 1000]

    # Benchmark directory
    benchmark_dir = Path(__file__).parent

    for num_inv in num_invs:

        # Run generic model
        generic_target = f"bench-tb_moslv_rf_inv_chain_N{num_inv}_tt_generic"
        run_benchmark(generic_target, args.REPEATS, args.j, benchmark_dir)

        # Run tailored model
        tailored_target = f"bench-tb_moslv_rf_inv_chain_N{num_inv}_tt_tailored"
        run_benchmark(tailored_target, args.REPEATS, args.j, benchmark_dir)


if __name__ == "__main__":
    sys.exit(main())
