from pathlib import Path
from breakdown_benchmark import BenchmarkSummary, BenchmarkComparison

if __name__ == "__main__":

    from base_generator import ModelType

    log_dir = Path("multiplier/logs/logs_laptop_Jun19_num_threads=2")
    out_dir = Path("multiplier/logs/logs_laptop_Jun19_num_threads=2/breakdown")
    out_dir.mkdir(parents=True, exist_ok=True)

    benchmark_base_name = f"tb_moslv_rf_c6288_tt"

    for model_type in [ModelType.GENERIC, ModelType.TAILORED_PARAMSET]:

        # Summarize
        benchmark_name = benchmark_base_name + f"_{model_type}.sp"
        summary = BenchmarkSummary(benchmark_name, log_dir, out_dir)
        summary.write_markdown_breakdown_table()

    # Compare
    comparison = BenchmarkComparison(benchmark_base_name, log_dir, out_dir)
    comparison.write_markdown_breakdown_comparison_table()
