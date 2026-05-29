from io import StringIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize
from matplotlib.pyplot import colormaps
from matplotlib.colors import LogNorm

from parse import split_nested_sweep, filter_data
from util import pointwise_rel_err
from dirs import *

fig_fsic_dir = fig_dir / "fsic"

ref_dir_fsic_sp = tests_dir_sp / "fsic"

def plot_tb_mos_id_vd(
        test_name,
        title,
        rel_err_ylim_min = None,
        show = False
    ):

    filepath_sp_paramset = ref_dir_fsic_sp / "ref" / (test_name + '.sp.out')
    filepath_sp_generic  = tests_dir_sp / "moslv" / "ref" / (test_name + '.sp.out')

    data_sp1 = pd.read_csv(filepath_sp_paramset, sep=r'\s+').values
    data_sp2 = pd.read_csv(filepath_sp_generic, sep=r'\s+').values

    id_curves_sp1, vd_arr_sp1, vg_arr_sp1 = split_nested_sweep(data_sp1, [2])
    id_curves_sp2, vd_arr_sp2, vg_arr_sp2 = split_nested_sweep(data_sp2, [2])
    assert np.allclose(vg_arr_sp1, vg_arr_sp2)
    assert np.allclose(vd_arr_sp1, vd_arr_sp2)
    vg_arr = vg_arr_sp1
    vd_arr = vd_arr_sp1

    fig = plt.figure(figsize=(8, 8))
    gs = plt.GridSpec(2, 1, bottom=0.2, left=0.2, hspace=0.3)
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)
    ax0.set_title(test_name)

    cmap = colormaps["spring"]
    norm = Normalize(vmin=vg_arr.min(), vmax=vg_arr.max())

    colors = cmap(norm(vg_arr))

    for i, (id_arr_sp1, id_arr_sp2, vg) in enumerate(zip(id_curves_sp1, id_curves_sp2, vg_arr)):

        ax0.plot(vd_arr, id_arr_sp1, c=colors[i], ls='-', label=f'{vg}')
        ax0.plot(vd_arr, id_arr_sp2, c='k', ls='--', label=f'generic' if i == len(vg_arr) - 1 else None)

        rel_abs_err_arr = pointwise_rel_err(id_arr_sp2, id_arr_sp1)
        ax1.semilogy(vd_arr, rel_abs_err_arr, c=colors[i], ls='-')

    fig.legend(title='V(g) [V]', ncol=len(vg_arr) + 1, bbox_to_anchor=(0.95, 0.1))

    ax0.set_title(title, fontsize=14)
    ax0.set_xlabel('V(d) [V]', fontsize=14)
    ax0.set_ylabel('I(d) [A]', fontsize=14)

    ax1.set_ylabel(r'$\varepsilon_{\mathrm{rel}}$', fontsize=18)
    ax1.set_xlabel('V(d) [V]', fontsize=14)

    if rel_err_ylim_min:
        ax1.set_ylim(ymin=rel_err_ylim_min)

    fig.align_ylabels()

    plt.savefig(fig_fsic_dir / (test_name + '.png'), dpi=300)

    if show:
        plt.show()

    plt.close()

    return

def plot_mos_inv_all_corners(ref_dir_gc, fig_dir, fig_name, show=False):

    corners = ['tt', 'ss', 'ff', 'sf', 'fs']
    fig, ax = plt.subplots(figsize=(10, 6))

    for corner in corners:
        filepath_gc = ref_dir_gc / f"tb_moslv_inv_{corner}.gc.out"

        data_gc_filt = filter_data(filepath_gc, skip_prefixes=('did not converge', 'open circuit'))
        data_gc = pd.read_csv(StringIO(data_gc_filt), sep=r'\s+', skipfooter=5, engine="python").values
        vin_gc, vout_gc = data_gc[:, 0], data_gc[:, 1]

        ax.plot(vin_gc, vout_gc, label=f'{corner.upper()}')

    ax.set_xlabel('V(in) [V]', fontsize=12)
    ax.set_ylabel('V(out) [V]', fontsize=12)
    ax.set_title('moslv CMOS inverter All Corners (Gnucap)', fontsize=14)
    ax.legend(title="Corners", fontsize=10)

    plt.tight_layout()
    plt.savefig(fig_fsic_dir / (fig_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()

    return

def plot_tb_nmos_id_vd(ng):
    plot_tb_mos_id_vd(
        f"tb_moslv_nmos_id_vd_ng{ng}",
        f"id-vd curves sg13g2_lv_nmos_psp ng={ng}")

def plot_tb_pmos_id_vd(ng):
    plot_tb_mos_id_vd(
        f"tb_moslv_pmos_id_vd_ng{ng}",
        f"id-vd curves sg13g2_lv_pmos_psp ng={ng}")

def plot_mos_inv(test_name, title, show=False):

    filepath_sp_paramset = ref_dir_fsic_sp / "ref" / (test_name + '.sp.out')
    filepath_sp_generic  = tests_dir_sp / "moslv" / "ref" / (test_name + '.sp.out')

    data_sp1 = pd.read_csv(filepath_sp_paramset, sep=r'\s+').values
    data_sp2 = pd.read_csv(filepath_sp_generic, sep=r'\s+').values

    vin_sp1, vout_sp1, idd_sp1 = data_sp1[:, 0], data_sp1[:, 1], data_sp1[:, 2]
    vin_sp2, vout_sp2, idd_sp2 = data_sp2[:, 0], data_sp2[:, 1], data_sp2[:, 2]

    assert np.allclose(vin_sp1, vin_sp2), "v(in) mismatch between gnucap and ngspice datasets"

    # Plotting setup
    plt.figure(figsize=(10, 8))
    gs = plt.GridSpec(2, 2)
    ax00 = plt.subplot(gs[0, 0])
    ax10 = plt.subplot(gs[1, 0])
    ax10.sharex(ax00)
    ax01 = plt.subplot(gs[0, 1])
    ax11 = plt.subplot(gs[1, 1])
    ax11.sharex(ax01)

    plt.suptitle(title, fontsize=14)

    ax00.plot(vin_sp1, vout_sp1, ls='-', color="blue" , label="paramset")
    ax00.plot(vin_sp2, vout_sp2, ls='--', color='k', label="generic")
    ax00.set_ylabel("V(out) [V]", fontsize=12)
    ax00.legend()

    ax01.plot(vin_sp1, -idd_sp1, ls='-', color="red"  , label="paramset")
    ax01.plot(vin_sp2, -idd_sp2, ls='--', color='k', label="generic")
    ax01.set_ylabel("I(DD) [A]", fontsize=12)
    ax01.legend()

    rel_abs_err = pointwise_rel_err(vout_sp1, vout_sp2)
    ax10.semilogy(vin_sp1, rel_abs_err, ls='-', color='k')
    ax10.set_xlabel("V(in) [V]", fontsize=12)
    ax10.set_ylabel(r"$\varepsilon_{\mathrm{rel}}$", fontsize=14)

    rel_abs_err = pointwise_rel_err(-idd_sp2, -idd_sp1)
    ax11.semilogy(vin_sp1, rel_abs_err, ls='-', color='k')
    ax11.set_xlabel("V(in) [V]", fontsize=12)
    ax11.set_ylabel(r"$\varepsilon_{\mathrm{rel}}$", fontsize=14)

    # Save and/or show the plot
    plt.tight_layout()
    plt.savefig(fig_fsic_dir / f"{test_name}.png", dpi=300)

    if show:
        plt.show()

    plt.close()

    return

def plot_tb_moslv_inv_tt():

    plot_mos_inv("tb_moslv_inv_tt", "moslv CMOS inverter tt corner")




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
    N_list = [50, 100, 500, 1000]

    cmap = plt.get_cmap('viridis')
    norm = LogNorm(vmin=min(N_list), vmax=max(N_list))

    fig = plt.figure(figsize=(10, 6))
    gs = plt.GridSpec(1, 1, bottom = 0.2)
    ax0 = plt.subplot(gs[0])

    vmid = 0.6

    for i, N in enumerate(N_list):

        filepath_sp_paramset = ref_dir_fsic_sp / "ref" / (f"tb_moslv_inv_chain_N{N}_tt" + '.sp.out')
        filepath_sp_generic  = tests_dir_sp / "moslv" / "ref" / (f"tb_moslv_inv_chain_N{N}_tt" + '.sp.out')

        data_sp1 = pd.read_csv(filepath_sp_paramset, sep=r'\s+').values
        data_sp2 = pd.read_csv(filepath_sp_generic, sep=r'\s+').values

        t_arr_sp1 = data_sp1[:, 0] / 1e-6
        vin_arr_sp1 =  data_sp1[:, 1]
        vout_arr_sp1 = data_sp1[:, 2]
        tout = crossing(t_arr_sp1, vout_arr_sp1, vmid, rising=(N % 2 == 0))

        t_arr_sp2 = data_sp2[:, 0] / 1e-6
        vout_arr_sp2 = data_sp2[:, 2]

        color = cmap(norm(N))

        ax0.plot(t_arr_sp1, vout_arr_sp1, ls="-", color=color, label=f"vout, N={N}")
        ax0.plot(tout, 0.6, marker = "o", color = color, zorder=5, ms=4)
        ax0.plot(t_arr_sp2, vout_arr_sp2, ls="--", color='k')

        if i == len(N_list) - 1:
            ax0.plot(t_arr_sp1, vin_arr_sp1, ls='--', color="k", alpha=0.5, label="vin")
            tin = crossing(t_arr_sp1, vin_arr_sp1, vmid, rising=True)
            ax0.plot(tin, 0.6, marker = "o", color = "k", zorder=5, alpha=0.5, ms=4)


    ax0.axhline(0.6, ls=":", lw=1.0, color="0.6", alpha=0.6)

    plt.tight_layout()
    ax0.set_xlabel("time [µs]")
    ax0.set_ylabel("voltage [V]")

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax0)
    cbar.set_label("Number of inverters N")

    # ax0.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=5, frameon=False)

    plt.savefig(fig_fsic_dir / (f"tb_moslv_inv_chain_tt" + ".png"), dpi=300)

    plt.legend()

    if show:
        plt.show()

    return

if __name__ == "__main__":

    # for ng in range(1, 5):
    #     plot_tb_nmos_id_vd(ng)
    #     plot_tb_pmos_id_vd(ng)
    #
    # plot_tb_moslv_inv_tt()

    plot_tb_moslv_inv_chain()

    print("Finished plotting fsic")
