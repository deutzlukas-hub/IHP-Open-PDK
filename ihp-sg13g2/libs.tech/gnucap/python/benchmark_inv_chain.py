from benchmark import Benchmarker
from dirs import tests_dir_sp

def benchmark_inv_chain():

    N_arr = [10, 50, 100, 500, 1000]
    test_names = [f"tb_moslv_inv_chain_N{N}_tt.sp" for N in N_arr]
    out_name = "bm_moslv_inv_chain_tt.csv"

    print("optimized osdi")
    fsic_dir = tests_dir_sp / "fsic"
    bm = Benchmarker(fsic_dir)
    bm.run(test_names, out_name )

    print("genric osdi")
    moslv_dir = tests_dir_sp / "moslv"
    bm = Benchmarker(moslv_dir)
    bm.run(test_names, out_name)


if __name__ == "__main__":

    benchmark_inv_chain()
