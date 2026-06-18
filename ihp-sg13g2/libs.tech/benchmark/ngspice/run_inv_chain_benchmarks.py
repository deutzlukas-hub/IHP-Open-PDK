#!/usr/bin/env python3
"""
Run inverter chain benchmarks for different chain sizes.

Runs make targets for both generic and tailored models with configurable repeats.
"""

import subprocess
import sys
from pathlib import Path


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

    # Configuration
    num_invs = [20, 200, 500, 1000]
    repeats = 7

    # Benchmark directory
    benchmark_dir = Path(__file__).parent


    for num_inv in num_invs:

        # Run generic model
        generic_target = f"bench-tb_moslv_rf_inv_chain_N{num_inv}_tt_generic"
        generic_success = run_benchmark(generic_target, repeats, 1, benchmark_dir)

        # Run tailored model
        tailored_target = f"bench-tb_moslv_rf_inv_chain_N{num_inv}_tt_tailored"
        tailored_success = run_benchmark(tailored_target, repeats, 1, benchmark_dir)


if __name__ == "__main__":
    sys.exit(main())
