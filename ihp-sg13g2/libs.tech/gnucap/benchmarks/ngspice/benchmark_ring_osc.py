from dirs import build_dir
from benchmark import Benchmarker
from base_generator import ModelType
from gen_ring_osc import RingOscillatorGenerator

def main():

    configs = [{"num_inv": num_inv} for num_inv in [11, 51, 101]]
    gen = RingOscillatorGenerator()
    bm = Benchmarker(build_dir, debug=True)

    for model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
        print("Benchmarking model type: ", model_type)
        out_name = f"bm_moslv_ring_osc_tt_{model_type}.csv"
        bm.run(gen, model_type, configs, out_name)
        print("")

if __name__ == "__main__":

    main()
