from dirs import build_dir
from benchmark import Benchmarker
from base_generator import ModelType
from gen_multiplier import C6288Generator

def benchmark_multiplier():

    gen = C6288Generator(tran_stop=2.0)
    bm = Benchmarker(build_dir, repeat=1)

    configs = []

    for model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
        print("Benchmarking model type: ", model_type)
        out_name = f"bm_multiplier_tt_{model_type}.csv"
        bm.run(gen, model_type, configs, out_name)
        print("")

if __name__ == "__main__":

    benchmark_multiplier()
