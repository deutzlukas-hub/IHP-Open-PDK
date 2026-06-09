import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LogNorm

from dirs import *

def crossing(t, v, level, rising=True):
    t = np.asarray(t)
    v = np.asarray(v)

    if rising:
        idx = np.where((v[:-1] < level) & (v[1:] >= level))[0][0]
    else:
        idx = np.where((v[:-1] > level) & (v[1:] <= level))[0][0]

    return t[idx] + (level - v[idx]) * (t[idx+1] - t[idx]) / (v[idx+1] - v[idx])

def plot_tb_moslv_inv_chain(show=False):

    # num inverters
    N_list = [10, 50, 100, 500, 1000]

    fig = plt.figure(figsize=(10, 10))
    gs = plt.GridSpec(3, 1, bottom = 0.1, hspace=0.4)
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1])
    ax2 = plt.subplot(gs[2])

    plt.suptitle("moslv CMOS inverter chain tt corner")

    # Colormap for N values
    cmap = plt.get_cmap('plasma')
    norm = LogNorm(vmin=min(N_list), vmax=max(N_list))

    # Plot transient waveforms
    vmid = 0.6
    for i, N in enumerate(N_list):

        test_name = f"tb_moslv_inv_chain_N{N}_tt"

        filepath_sp_gener = ref_dir_sp / (f"{test_name}" +  "_generic"   + '.sp.out')
        filepath_sp_param = ref_dir_sp / (f"{test_name}" +  "_paramset"   + '.sp.out')

        data_sp1 = pd.read_csv(filepath_sp_param, sep=r'\s+').values
        data_sp2 = pd.read_csv(filepath_sp_gener, sep=r'\s+').values

        t_arr_sp1 = data_sp1[:, 0] / 1e-6
        vin_arr_sp1 =  data_sp1[:, 1]
        vout_arr_sp1 = data_sp1[:, 2]
        tout = crossing(t_arr_sp1, vout_arr_sp1, vmid, rising=(N % 2 == 0))

        t_arr_sp2 = data_sp2[:, 0] / 1e-6
        vout_arr_sp2 = data_sp2[:, 2]

        color = cmap(norm(N))

        ax0.plot(t_arr_sp1, vout_arr_sp1, ls="-", color=color, lw = 2.0, label=f"vout, N={N}")
        ax0.plot(t_arr_sp2, vout_arr_sp2, ls="--", color='k', lw = 1.0)
        ax0.plot(tout, 0.6, marker = "o", color = color, zorder=5, ms=4)

        if i == len(N_list) - 1:
            ax0.plot(t_arr_sp1, vin_arr_sp1, ls='-', color="grey", alpha=1.0, lw = 2.0, label="vin")
            tin = crossing(t_arr_sp1, vin_arr_sp1, vmid, rising=True)
            ax0.plot(tin, 0.6, marker = "o", color = "grey", zorder=5, alpha=1.0, ms=4)
            ax0.text(0.6 * tin, 0.59, "input", color="0.45", fontsize=9, ha="center")

    ax0.axhline(0.6, ls=":", lw=1.0, color="0.6", alpha=0.6)
    ax0.set_xlabel("time [µs]")
    ax0.set_ylabel("voltage [V]")

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax0)
    cbar.set_label("Number of inverters N")

    # Read benchmark dataruntime
    filepath_sp_param = bm_dir_sp / f"bm_moslv_inv_chain_tt_generic.csv"
    filepath_sp_gener = bm_dir_sp / f"bm_moslv_inv_chain_tt_paramset.csv"

    df_sp_param = pd.read_csv(filepath_sp_param)
    df_sp_gener = pd.read_csv(filepath_sp_gener)

    df_sp_param['N'] = df_sp_param['test'].str.extract(r'N(\d+)').astype(int)
    df_sp_gener['N'] = df_sp_gener['test'].str.extract(r'N(\d+)').astype(int)

    # Merge on N to ensure alignment
    merged = pd.merge(
        df_sp_param[['N', 'median_s']],
        df_sp_gener[['N', 'median_s']],
        on='N',
        suffixes=('_param', '_gener')
    ).sort_values('N')

    # Extract aligned data
    N_arr = merged['N'].values
    median_s_param = merged['median_s_param'].values
    median_s_gener = merged['median_s_gener'].values

    speedup = median_s_param / median_s_gener

    # plot median runtime time
    ax1.semilogx(N_arr, median_s_param, "-o", color="blue", lw = 2.0, label="paramset osdi")
    ax1.semilogx(N_arr, median_s_gener, "-o", color="red", lw = 2.0, label="generic osdi")
    ax1.set_ylabel("Median Runtime [s]", fontsize=12)
    ax1.set_xlabel("Number of inverters N", fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # plot speedup
    ax2.semilogx(N_list, speedup, "-o", c='k', lw=2.0)
    ax2.axhline(1.0, ls='--', color='k', lw=1, alpha=0.5)
    ax2.set_ylabel("Speedup Ratio\n(Paramset / Generic )", fontsize=12)
    ax2.set_xlabel("Number of inverters N", fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.legend()

    plt.savefig(fig_sp / (f"tb_moslv_inv_chain_tt" + ".png"), dpi=300)

    if show:
        plt.show()

    return

def main():
    plot_tb_moslv_inv_chain()

if __name__ == "__main__":
    main()



