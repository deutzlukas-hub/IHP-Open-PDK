from dirs import build_dir
from benchmark import Benchmarker
from base_generator import ModelType
from gen_ring_osc import RingOscillatorGenerator

def main():

    # Average propagation delay
    tpd = 0.15679572639369496 * 1e-9
    num_cycles = 20
    points_per_cycle = 100

    configs = []

    for num_inv in [11, 51, 101]:
        T = 2 * num_inv * tpd

        configs.append(
            {
            "num_inv": num_inv,
            "tran_stop": num_cycles * T,
            "tran_step": T / points_per_cycle,
            "tran_max": T / points_per_cycle,
        }
        )

    gen = RingOscillatorGenerator()
    bm = Benchmarker(build_dir, debug=True)

    for model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
        print("Benchmarking model type: ", model_type)
        out_name = f"bm_moslv_ring_osc_tt_{model_type}.csv"
        bm.run(gen, model_type, configs, out_name)
        print("")

if __name__ == "__main__":

    main()
