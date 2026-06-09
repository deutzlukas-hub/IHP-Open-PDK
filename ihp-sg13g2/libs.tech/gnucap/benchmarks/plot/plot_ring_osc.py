import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from dirs import *

def rising_crossings(t_arr, v_arr, threshold):

    t_arr = np.asarray(t_arr)
    v_arr = np.asarray(v_arr)

    idx = np.where((v_arr[:-1] < threshold) & (v_arr[1:] >= threshold))[0]
    crossings = np.zeros_like(idx, dtype=float)

    for j, i in enumerate(idx):
        # linear interpolation
        frac = (threshold - v_arr[i]) / (v_arr[i + 1] - v_arr[i])
        crossings[j] = t_arr[i] + frac * (t_arr[i + 1] - t_arr[i])

    return np.asarray(crossings)

def estimate_ring_tpd(t_arr, v_arr, num_inv, vdd=1.2, skip_cycles=2):

    crossings = rising_crossings(t_arr, v_arr, vdd / 2)

    # discard startup cycles
    assert len(crossings) >= skip_cycles + 2, "not enough crossings to estimate period"
    crossings = crossings[skip_cycles:]

    periods = np.diff(crossings)
    period = periods.mean()
    frequency = 1 / period
    tpd = period / (2 * num_inv)

    return tpd

def estimate_ring_tpd_from_data():

    num_inv = 11
    filepath_sp_param = ref_dir_sp / f"tb_moslv_ring_osc_N{num_inv}_tt.sp.out"
    data_sp = pd.read_csv(filepath_sp_param, sep=r'\s+').values
    t_arr = data_sp[:, 0] / 1e-9
    vout_arr = data_sp[:, 1]
    tpd = estimate_ring_tpd(t_arr, vout_arr, num_inv)
    print(tpd)

def plot_tb_moslv_ring_osc(show: bool=False):

    # num inverters
    num_inv_list = [11, 51, 101]

    fig = plt.figure(figsize=(10, 10))
    gs = plt.GridSpec(len(num_inv_list) + 2, 1, bottom = 0.1, hspace=0.4)

    # Colormap for N values
    cmap = plt.get_cmap('plasma')
    norm = LogNorm(vmin=min(num_inv_list), vmax=max(num_inv_list))

    for i, num_inv in enumerate(num_inv_list):

        ax_i = plt.subplot(gs[i])

        filepath_sp_gener = ref_dir_sp / f"tb_moslv_ring_osc_N{num_inv}_tt_generic.sp.out"
        filepath_sp_param = ref_dir_sp / f"tb_moslv_ring_osc_N{num_inv}_tt_paramset.sp.out"

        data_sp_param = pd.read_csv(filepath_sp_param, sep=r'\s+').values
        data_sp_gener = pd.read_csv(filepath_sp_gener, sep=r'\s+').values

        t_arr_sp_param = data_sp_param[:, 0] / 1e-9
        t_arr_sp_gener = data_sp_gener[:, 0] / 1e-9

        vout_arr_param = data_sp_param[:, 1]
        vout_arr_gener = data_sp_gener[:, 1]

        color = cmap(norm(num_inv))

        ax_i.plot(t_arr_sp_param, vout_arr_param, ls="-", color=color, lw=2.0, label=f"vout, N={num_inv}")
        ax_i.plot(t_arr_sp_gener, vout_arr_gener, ls="--", color="k", lw=2.0, label=f"vout, N={num_inv}")

    # Read benchmark dataruntime
    filepath_sp_param = bm_dir_sp / f"bm_moslv_ring_osc_tt_generic.csv"
    filepath_sp_gener = bm_dir_sp / f"bm_moslv_ring_osc_tt_paramset.csv"

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

    ax1 = plt.subplot(gs[len(num_inv_list)])
    ax2 = plt.subplot(gs[len(num_inv_list)+1])

    # plot median runtime time
    ax1.semilogx(N_arr, median_s_param, "-o", color="blue", lw = 2.0, label="paramset osdi")
    ax1.semilogx(N_arr, median_s_gener, "-o", color="red", lw = 2.0, label="generic osdi")
    ax1.set_ylabel("Median Runtime [s]", fontsize=12)
    ax1.set_xlabel("Number of inverters N", fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # plot speedup
    ax2.semilogx(N_arr, speedup, "-o", c='k', lw=2.0)
    ax2.axhline(1.0, ls='--', color='k', lw=1, alpha=0.5)
    ax2.set_ylabel("Speedup Ratio\n(Paramset / Generic )", fontsize=12)
    ax2.set_xlabel("Number of inverters N", fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.legend()

    plt.savefig(fig_sp / (f"tb_moslv_ring_osc_tt" + ".png"), dpi=300)

    if show:
        plt.show()

if __name__ == "__main__":

    plot_tb_moslv_ring_osc()
