from dirs import build_dir
from benchmark import Benchmarker
from base_generator import ModelType
from gen_inv_chain import InverterChainGenerator

def benchmark_inv_chain():

    configs = [{"num_inv": num_inv} for num_inv in [10, 50, 100, 500, 1000]]
    gen = InverterChainGenerator()
    bm = Benchmarker(build_dir)

    for model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
        out_name = f"bm_moslv_inv_chain_tt_{model_type}.csv"
        bm.run(gen, model_type, configs, out_name)

if __name__ == "__main__":
    benchmark_inv_chain()
