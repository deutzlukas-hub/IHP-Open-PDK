from dataclasses import dataclass
import re
from pathlib import Path
import statistics as stats

from base_generator import ModelType

@dataclass
class BenchmarkMetrics:
    # Overall runtime
    total_elapsed_time: float
    total_analysis_time: float
    transient_analysis_time: float
    # Circuit / matrix complexity
    circuit_equations: float
    original_nonzeros: float
    fill_in_nonzeros: float
    total_nonzeros: float
    # Device eval / matrix load:
    matrix_load_time: float
    transient_load_time: float
    # Matrix solve:
    matrix_synchronize_time: float
    matrix_reorder_time: float
    matrix_factor_time: float
    matrix_solve_time: float
    transient_factor_time: float
    transient_solve_time: float
    # Transient timestep control
    transient_trunc_time: float

@dataclass
class MetricStats:
    minimum: float
    median: float
    mean: float
    maximum: float
    stdev: float
    stdev_percent: float
    max_deviation_percent: float
    n: int
    share_median_percent: float | None = None
    share_mean_percent: float | None = None

@dataclass
class MetricStatsSummary:
    value: MetricStats
    share: MetricStats | None = None

@dataclass
class BenchmarkRun:
    index: int
    log_file: Path
    metrics: BenchmarkMetrics

class BenchmarkSummary:

    METRIC_TO_LOG_LABEL = {
        "total_elapsed_time": "Total elapsed time (seconds)",
        "total_analysis_time": "Total analysis time (seconds)",
        "transient_analysis_time": "Transient analysis time",
        "circuit_equations": "Circuit Equations",
        "original_nonzeros": "Circuit original non-zeroes",
        "fill_in_nonzeros": "Circuit fill-in non-zeroes",
        "total_nonzeros": "Circuit total non-zeroes",
        "matrix_load_time": "Matrix load time",
        "transient_load_time": "Transient load time",
        "matrix_synchronize_time": "Matrix synchronize time",
        "matrix_reorder_time": "Matrix reorder time",
        "matrix_factor_time": "Matrix factor time",
        "matrix_solve_time": "Matrix solve time",
        "transient_factor_time": "Transient factor time",
        "transient_solve_time": "Transient solve time",
        "transient_trunc_time": "Transient trunc time",
    }

    DERIVED_METRICS = {
        "matrix_solve_total_time",
    }

    SHARE_DENOMINATOR_BY_METRIC = {
        "total_analysis_time": "total_elapsed_time",
        "matrix_load_time": "total_analysis_time",
        "matrix_solve_total_time": "total_analysis_time",
        "matrix_synchronize_time": "matrix_solve_total_time",
        "matrix_reorder_time": "matrix_solve_total_time",
        "matrix_factor_time": "matrix_solve_total_time",
        "matrix_solve_time": "matrix_solve_total_time",
    }

    def __init__(self,
        benchmark_name: str,
        log_dir: Path,
        out_dir: Path | None = None
    ):
        self.benchmark_name = benchmark_name
        self.log_dir = log_dir
        self.out_dir = out_dir

        self.runs: list[BenchmarkRun]= self._parse_runs()
        self.summary_by_metric: dict[str, MetricStatsSummary] = self.compute_summary_by_metric()

    def write_markdown_breakdown_table(self) -> Path:

        outfile = self.out_dir / f"{self.benchmark_name}.breakdown.md"
        outfile.write_text(self.to_markdown_breakdown_table())

        return outfile

    def compute_summary_by_metric(self) -> dict[str, MetricStatsSummary]:

        summary_by_metric = {}

        for metric_name in list(self.METRIC_TO_LOG_LABEL) + list(self.DERIVED_METRICS):

            value_stats = self.compute_metric_stats(metric_name)
            share_stats = self.compute_share_stats(metric_name)

            summary_by_metric[metric_name] = MetricStatsSummary(value_stats, share_stats)

        return summary_by_metric

    def compute_metric_stats(self, metric_name) -> MetricStats:

        values = [self._get_metric_value(run, metric_name) for run in self.runs]

        return self.compute_stats(values)

    def compute_share_stats(self, metric_name: str) -> MetricStats:

        denominator_metric = self.SHARE_DENOMINATOR_BY_METRIC.get(metric_name)

        if denominator_metric is None:
            return None

        values = []

        for run in self.runs:
            numerator = self._get_metric_value(run, metric_name)
            denominator = self._get_metric_value(run, denominator_metric)

            assert denominator != 0, "denominator should not be zero"
            assert numerator < denominator, "numerator should not be greater than denominator"

            values.append(numerator / denominator * 100.0)

        return self.compute_stats(values)

    def compute_stats(self, values: list[float]) -> MetricStats | None:

        mean = stats.mean(values)
        stdev = stats.stdev(values) if len(values) > 1 else 0.0

        if mean != 0:
            stdev_percent = stdev / mean * 100.0
            max_deviation_percent = max(abs(value - mean) for value in values) / mean * 100.0
        else:
            stdev_percent = 0.0
            max_deviation_percent = 0.0

        return MetricStats(
            minimum=min(values),
            median=stats.median(values),
            mean=mean,
            maximum=max(values),
            stdev=stdev,
            stdev_percent=stdev_percent,
            max_deviation_percent=max_deviation_percent,
            n=len(values),
        )

    def _get_metric_value(self, run: BenchmarkRun, metric_name: str) -> float:

        if metric_name == "matrix_solve_total_time":
            return (
                    run.metrics.matrix_synchronize_time
                    + run.metrics.matrix_reorder_time
                    + run.metrics.matrix_factor_time
                    + run.metrics.matrix_solve_time
            )

        return getattr(run.metrics, metric_name)

    def _run_index(self, log_file) -> int:
        return int(log_file.name.removesuffix(".log").split(".")[-1])

    def _parse_runs(self):

        indexed_log_files = [
            (self._run_index(log_file), log_file)
            for log_file in self.log_dir.glob(f"{self.benchmark_name}.*.log")
        ]

        indexed_log_files.sort(key=lambda x: x[0])

        runs = [
            self._parse_benchmark_log(run_index, log_file)
            for run_index, log_file in indexed_log_files
        ]

        return runs

    def _parse_benchmark_log(self, run_index: int, log_file: Path):

        log_text = log_file.read_text()

        values = {}

        for metric, label in self.METRIC_TO_LOG_LABEL.items():

            pattern = rf"^{re.escape(label)}\s*=\s*(?P<value>[-+0-9.eE]+)"
            match = re.search(pattern, log_text, re.MULTILINE)

            if not match:
                raise ValueError(f"Could not find metric: {label} in log {log_file}")

            values[metric] = float(match.group("value"))

        metrics = BenchmarkMetrics(**values)

        return BenchmarkRun(run_index, log_file, metrics)

    def to_markdown_breakdown_table(self):

        rows = [
            ("**Overall runtime**", None),
            ("Total elapsed time", "total_elapsed_time"),
            ("Total analysis time","total_analysis_time"),

            ("**Circuit / matrix complexity**", None),
            ("Circuit equations", "circuit_equations"),
            ("Original non-zeroes", "original_nonzeros"),
            ("Fill-in non-zeroes", "fill_in_nonzeros"),
            ("Total non-zeroes", "total_nonzeros"),

            ("**Analysis time breakdown**", None),
            ("Total analysis time", "total_analysis_time"),
            ("Matrix load time", "matrix_load_time"),
            ("Matrix solve total", "matrix_solve_total_time"),

            ("**Matrix solve breakdown**", None),
            ("Matrix solve total", "matrix_solve_total_time"),
            ("Matrix synchronize time", "matrix_synchronize_time"),
            ("Matrix factor time", "matrix_factor_time"),
            ("Matrix reorder time", "matrix_reorder_time"),
            ("Matrix solve time", "matrix_solve_time"),
            #("Transient factor time", "transient_factor_time"),
            #("Transient solve time", "transient_solve_time"),
            #("**Transient timestep control**", None),
            #("Transient trunc time", "transient_trunc_time"),
        ]

        count_metrics = {
            "circuit_equations",
            "original_nonzeros",
            "fill_in_nonzeros",
            "total_nonzeros",
        }

        def fmt_value(metric_name: str, value: float) -> str:
            if metric_name in count_metrics:
                return f"{value:,.0f}"
            return f"{value:.4f}"

        def fmt_percent(value: float) -> str:
            return f"{value:.1f}%"

        lines = [
            f"### {self.benchmark_name}",
            "",
            f"Runs: {len(self.runs)}",

            "| Metric (runs={}) | Median (s) | Mean (s) | Max dev. % | Median share %",
            "|---|---:|---:|---:|---:|",
        ]

        for label, metric_name in rows:
            if metric_name is None:
                lines.append(f"| {label} |  |  |  |  |")
                continue

            metric_summary = self.summary_by_metric[metric_name]

            lines.append(
                f"| {label} | "
                f"{fmt_value(metric_name, metric_summary.value.median)} | "
                f"{fmt_value(metric_name, metric_summary.value.mean)} | "
                f"{fmt_percent(metric_summary.value.max_deviation_percent)} |"
                f"{fmt_percent(metric_summary.share.median) if metric_summary.share else '—'} |"
            )

        return "\n".join(lines)


class BenchmarkComparison():

    COUNT_METRICS = {
        "circuit_equations",
        "original_nonzeros",
        "fill_in_nonzeros",
        "total_nonzeros",
    }


    def __init__(
        self,
        benchmark_name_base:
        str, log_dir: Path,
        out_dir: Path | None = None
    ):

        self.benchmark_base_name = benchmark_name_base
        self.log_dir = log_dir
        self.out_dir = out_dir

        generic_name = benchmark_name_base + "_" + ModelType.GENERIC + ".sp"
        tailored_name = benchmark_name_base + "_" + ModelType.TAILORED_PARAMSET + ".sp"

        self.generic_summary = BenchmarkSummary(generic_name, log_dir, out_dir)
        self.tailored_summary = BenchmarkSummary(tailored_name, log_dir, out_dir)

    def fmt_value(self, metric_name: str, value: float) -> str:
        if metric_name in self.COUNT_METRICS:
            return f"{value:,.0f}"
        return f"{value:.4f}"

    @staticmethod
    def fmt_percent(value: float) -> str:
        return f"{value:.1f}%"

    def fmt_difference(self, generic_value: float, tailored_value: float) -> str:
        if generic_value == 0:
            return "—"

        return self.fmt_percent(
            (generic_value - tailored_value) / generic_value * 100.0
        )

    def fmt_speedup(
        self,
        metric_name: str,
        generic_value: float,
        tailored_value: float,
    ) -> str:
        if metric_name in self.COUNT_METRICS:
            return "—"

        if tailored_value == 0:
            return "—"

        return f"{generic_value / tailored_value:.2f}×"

    def to_markdown_comparison_table(self) -> Path:

        rows = [
            ("**Overall runtime**", None),
            ("Total elapsed time", "total_elapsed_time"),
            ("Total analysis time","total_analysis_time"),

            ("**Circuit / matrix complexity**", None),
            ("Circuit equations", "circuit_equations"),
            ("Original non-zeroes", "original_nonzeros"),
            ("Fill-in non-zeroes", "fill_in_nonzeros"),
            ("Total non-zeroes", "total_nonzeros"),

            ("**Analysis time breakdown**", None),
            ("Total analysis time", "total_analysis_time"),
            ("Matrix load time", "matrix_load_time"),
            ("Matrix solve total", "matrix_solve_total_time"),

            ("**Matrix solve breakdown**", None),
            ("Matrix solve total", "matrix_solve_total_time"),
            ("Matrix synchronize time", "matrix_synchronize_time"),
            ("Matrix factor time", "matrix_factor_time"),
            ("Matrix reorder time", "matrix_reorder_time"),
            ("Matrix solve time", "matrix_solve_time"),
        ]

        lines = [
            f"### Generic vs tailored: `{self.benchmark_base_name}`",
            "",
            f"Generic runs: {len(self.generic_summary.runs)}",
            f"Tailored runs: {len(self.tailored_summary.runs)}",
            "",
            "| Metric | Generic median | Tailored median | Difference | Speedup |",
            "|---|---:|---:|---:|---:|",
        ]

        for label, metric_name in rows:
            if metric_name is None:
                lines.append(f"| {label} |  |  |  |  |")
                continue

            generic_value = self.generic_summary.summary_by_metric[metric_name].value.median
            tailored_value = self.tailored_summary.summary_by_metric[metric_name].value.median

            lines.append(
                f"| {label} | "
                f"{self.fmt_value(metric_name, generic_value)} | "
                f"{self.fmt_value(metric_name, tailored_value)} | "
                f"{self.fmt_difference(generic_value, tailored_value)} | "
                f"{self.fmt_speedup(metric_name, generic_value, tailored_value)} |"
            )

        return "\n".join(lines)


    def write_markdown_breakdown_comparison_table(self) -> Path:

        outfile = self.out_dir / f"{self.benchmark_base_name}.breakdown.comparison.md"
        outfile.write_text(self.to_markdown_comparison_table())

        return outfile

if __name__ == "__main__":

    from base_generator import ModelType

    num_inv_list = [20, 50, 100, 200, 500]

    log_dir = Path("./inv_chain/logs_from_ihp_Jun19")
    out_dir = Path("./inv_chain/logs_from_ihp_Jun19/breakdown")
    out_dir.mkdir(parents=True, exist_ok=True)

    for model_type in [ModelType.GENERIC, ModelType.TAILORED_PARAMSET]:
        for num_inv in num_inv_list:
            # benchmark_name = f"tb_moslv_rf_inv_chain_N{num_inv}_tt_{model_type}.sp"
            # log_dir = Path("./inv_chain/logs_from_ihp_Jun19")
            # out_dir = Path("./inv_chain/logs_from_ihp_Jun19/breakdown")
            # summary = BenchmarkSummary(benchmark_name, log_dir, out_dir)
            # summary.write_markdown_breakdown_table()

            benchmark_base_name = f"tb_moslv_rf_inv_chain_N{num_inv}_tt"

            comparison = BenchmarkComparison(benchmark_base_name, log_dir, out_dir)
            comparison.write_markdown_breakdown_comparison_table()

