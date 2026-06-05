import os
import timeit
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import statistics as stats
import csv


class Benchmarker():

    def __init__(self, test_dir: Path, repeat: int = 5, number: int = 1):
        self.test_dir = test_dir
        self.bm_dir = test_dir / "bm"

        self.repeat = repeat
        self.number = number

    @staticmethod
    def write_csv(results: list[dict], out_path: Path) -> None:

        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"wrote {out_path}")

    def run_ngspice(self, test_name) -> None:

        proc = subprocess.run(
            ["ngspice", "-b", test_name],
            cwd=self.test_dir,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"ngspice failed {proc.returncode}")


    def benchmark(self, test_name: str) -> dict:

        print(f"→ {test_name}: STARTED")

        times = timeit.repeat(
                stmt = lambda: self.run_ngspice(test_name),
                repeat = self.repeat,
                number= self.number
        )

        return {
            "test": test_name,
            "runs": self.repeat,
            "min_s": min(times),
            "median_s": stats.median(times),
            "mean_s": stats.mean(times),
            "stdev_s": stats.stdev(times) if self.repeat > 1 else 0.0,
        }

    def benchmark_many(
        self,
        test_names: list[str],
        workers: int | None = None
    ) -> list[dict]:

        if workers is None: workers = min(len(test_names), os.cpu_count())

        num_tests = len(test_names)

        print(f"Starting {num_tests} benchmarks with {workers} workers...")

        results = []

        with (ThreadPoolExecutor(max_workers=workers) as pool):

            futures = {pool.submit(self.benchmark, tn): tn for tn in test_names}

            completed = 1

            for future in as_completed(futures):
                test_name = futures[future]
                try:
                    result = future.result()
                    results.append(result)


                    print(
                        f"✓ [{completed}/{num_tests}] {test_name}: FINISHED "
                        f"median={result['median_s']:.3f}s "
                        f"min={result['min_s']:.3f}s"
                    )

                except Exception as err:
                    print(
                        f"x [{completed}/{num_tests}]: {test_name}: "
                        f"FAILED with ERR: {err}"
                    )
                completed += 1

        return sorted(results, key=lambda r: r["test"])

    def run(self,
            test_names: list[str],
            out_name: str,
            workers: int | None = None
        ) -> Path:

        self.bm_dir.mkdir(exist_ok=True)
        out_path = self.bm_dir / out_name

        results = self.benchmark_many(test_names, workers=workers)
        Benchmarker.write_csv(results, out_path)

        return out_path
