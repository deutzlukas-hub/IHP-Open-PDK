from pathlib import Path
from breakdown_benchmark import BenchmarkSummary, BenchmarkComparison

if __name__ == "__main__":

    from base_generator import ModelType

    num_inv_list = [20, 50, 100, 200, 500]

    log_dir = Path("./inv_chain/logs_from_ihp_Jun19")
    out_dir = Path("./inv_chain/logs_from_ihp_Jun19/breakdown")
    out_dir.mkdir(parents=True, exist_ok=True)

    for model_type in [ModelType.GENERIC, ModelType.TAILORED_PARAMSET]:
        for num_inv in num_inv_list:

            # Summarize
            benchmark_name = f"tb_moslv_rf_inv_chain_N{num_inv}_tt_{model_type}.sp"
            log_dir = Path("./inv_chain/logs_from_ihp_Jun19")
            out_dir = Path("./inv_chain/logs_from_ihp_Jun19/breakdown")
            summary = BenchmarkSummary(benchmark_name, log_dir, out_dir)
            summary.write_markdown_breakdown_table()

            # Compare
            benchmark_base_name = f"tb_moslv_rf_inv_chain_N{num_inv}_tt"
            comparison = BenchmarkComparison(benchmark_base_name, log_dir, out_dir)
            comparison.write_markdown_breakdown_comparison_table()

