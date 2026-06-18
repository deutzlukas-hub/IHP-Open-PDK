import argparse
import subprocess
from pathlib import Path

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

def run_benchmark(target: str, j: int = 1, repeats: int = 7, cwd: Path = None) -> bool:


    subprocess.run(
        ["make", target, f"-j{j}", f"REPEATS={repeats}"],
        cwd=cwd,
        check=True,
        text=True
    )
