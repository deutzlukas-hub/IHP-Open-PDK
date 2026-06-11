import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from dirs import ngspice_dir, fig_dir

mult_dir = ngspice_dir / "multiplier"
ref_dir = mult_dir / "ref"
bm_dir = mult_dir / "bm"

def read_wrdata(filepath, n_a=16, n_b=16, n_p=32):

    filepath = Path(filepath)

    df = pd.read_csv(filepath, sep=r"\s+")
    arr = df.to_numpy(dtype=float)

    t = arr[:, 0]
    vecs = arr[:, 1:]

    a = vecs[:, 0:n_a]
    b = vecs[:, n_a:n_a + n_b]
    p = vecs[:, n_a + n_b:n_a + n_b + n_p]

    return t, a, b, p

def plot_tb_moslv_c6288_multiplier(
    show=False,
    test_name="tb_moslv_c6288_tt",
    vdd=1.2
):
    """Plot C6288 16x16 multiplier output comparison.

    Expected files:
        ref_dir_sp / f"{test_name}_paramset.sp.out"
        ref_dir_sp / f"{test_name}_generic.sp.out"

    Expected wrdata order:
        a[0:15], b[0:15], p[0:31], optional i(VDD)
    """

    filepath_sp_param = ref_dir / f"{test_name}_paramset.sp.out"
    filepath_sp_gener = ref_dir / f"{test_name}_generic.sp.out"
    filepath_sp_taylo = ref_dir / f"{test_name}_taylored.sp.out"

    t_param, a_param, b_param, p_param = read_wrdata(filepath_sp_param)
    t_gener, a_gener, b_gener, p_gener = read_wrdata(filepath_sp_gener)
    t_taylo, a_taylo, b_taylo, p_taylo = read_wrdata(filepath_sp_taylo)


    t_param *= 1e9
    t_gener *= 1e9
    t_taylo *= 1e9

    nodes = [0, 15, 31]

    gs = plt.GridSpec(len(nodes), 1, hspace=0.3)

    for i, node in enumerate(nodes):
        ax = plt.subplot(gs[i])

        ax.plot(t_gener, p_gener[:, node], ls='-', lw=3.0, c='k', label="generic")
        ax.plot(t_param, p_param[:, node], c = 'r', ls = "--", lw=2.0, label="paramset")
        ax.plot(t_taylo, p_taylo[:, node], c = 'b', ls = ':' , lw =2.0, label="taylored")

        ax.set_ylabel(f"p[{node}]")
        ax.legend()

    if show:
        plt.show()

    plt.savefig(fig_dir / (f"tb_moslv_c6288_tt" + ".png"), dpi=300)

    return

def main():
    plot_tb_moslv_c6288_multiplier()


if __name__ == "__main__":

    main()
