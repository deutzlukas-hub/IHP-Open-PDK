from pathlib import Path
from io import StringIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.pyplot import colormaps

from parse import filter_data, split_nested_sweep
from util import pointwise_rel_err

base_dir = Path(__file__).resolve().parent.parent

test_dir = base_dir / "tests"
fig_dir = base_dir / "figures"
ref_dir = test_dir / "ref"


def plot_tb_mos_id_vd(
        test_names,
        title,
        rel_err_ylim_min = None,
        show = False
    ):

    test_keys = list(test_names.keys())
    filepaths = [ref_dir / (test_name + '.sp.out') for test_name in test_names.values()]
    data_list = [pd.read_csv(filepath, sep=r'\s+').values for filepath in filepaths]

    test_keys.pop(0)
    data_ref = data_list.pop(0)
    test_name = list(test_names.values())[0]

    id_curves, vd_arr, vg_arr = split_nested_sweep(data_ref, [2])

    fig = plt.figure(figsize=(6 * len(data_list), 8))
    gs = plt.GridSpec(2, len(data_list), bottom=0.2, left=0.2, hspace=0.3)

    cmap = colormaps["spring"]
    norm = Normalize(vmin=vg_arr.min(), vmax=vg_arr.max())

    colors = cmap(norm(vg_arr))

    for i, data in enumerate(data_list):

        ax0 = plt.subplot(gs[0, i])
        ax1 = plt.subplot(gs[1, i], sharex=ax0)
        ax0.set_title(test_keys[i], fontsize=14)

        id_curves_i, vd_arr_i, vg_arr_i = split_nested_sweep(data, [2])

        assert np.allclose(vg_arr, vg_arr_i)
        assert np.allclose(vd_arr, vd_arr_i)

        for j, (id_arr_i, id_arr, vg) in enumerate(zip(id_curves_i, id_curves, vg_arr)):

            ax0.plot(vd_arr, id_arr_i, c=colors[j], ls='-', lw=2.0, label=f'{vg}' if (j == 0 and i==0) else None)
            ax0.plot(vd_arr, id_arr, c="k", ls='--', lw=1.0)

            rel_abs_err_arr = pointwise_rel_err(id_arr, id_arr_i)

            if np.allclose(rel_abs_err_arr, np.zeros_like(rel_abs_err_arr)):
                ax1.plot(vd_arr, rel_abs_err_arr, c=colors[i], ls='--')
            else:
                ax1.semilogy(vd_arr, rel_abs_err_arr, c=colors[i], ls='--')

    fig.legend(title='V(g) [V]', ncol=len(vg_arr) + 1, bbox_to_anchor=(0.95, 0.1))

    plt.suptitle(title, fontsize=14)

    ax0.set_xlabel('V(d) [V]', fontsize=14)
    ax0.set_ylabel('I(d) [A]', fontsize=14)

    ax1.set_ylabel(r'$\varepsilon_{\mathrm{rel}}$', fontsize=18)
    ax1.set_xlabel('V(d) [V]', fontsize=14)

    if rel_err_ylim_min:
        ax1.set_ylim(ymin=rel_err_ylim_min)

    fig.align_ylabels()

    plt.savefig(fig_dir / (test_name + '.png'), dpi=300)

    if show:
        plt.show()

    plt.close()

    return


def plot_tb_nmos_id_vd_ng():

    test_names = {
        "generic": "tb_moslv_nmos_id_vd_ng1",
        "dump.cleaned": "tb_moslv_nmos_id_vd_ng1.dump.cleaned",
        "dump.pruned": "tb_moslv_nmos_id_vd_ng1.dump.pruned",
        "dump.renamed": "tb_moslv_nmos_id_vd_ng1.dump.renamed",
        "dump.pruned.renamed.cleaned": "tb_moslv_nmos_id_vd_ng1.dump.pruned.renamed.cleaned"
    }

    plot_tb_mos_id_vd(
        test_names,
        f"id-vd curves sg13g2_lv_nmos_psp ng=1",
    )

def plot_tb_nmos_id_vd_ng_optimized():

    test_names = {
        "dump.pruned.renamed.cleaned": "tb_moslv_nmos_id_vd_ng1.dump.pruned.renamed.cleaned",
        "dump.pruned.renamed.cleaned.optimized": "tb_moslv_nmos_id_vd_ng1.dump.pruned.renamed.cleaned.optimized"
    }

    plot_tb_mos_id_vd(
        test_names,
        f"id-vd curves sg13g2_lv_nmos_psp ng=1",
        fig_dir
    )

def plot_tb_pmos_id_vd_ng():

    test_names = {
        "generic": "tb_moslv_pmos_id_vd_ng1",
        "dump.cleaned": "tb_moslv_pmos_id_vd_ng1.dump.cleaned",
        "dump.pruned": "tb_moslv_pmos_id_vd_ng1.dump.pruned",
        "dump.renamed": "tb_moslv_pmos_id_vd_ng1.dump.renamed",
        "dump.pruned.renamed.cleaned": "tb_moslv_pmos_id_vd_ng1.dump.pruned.renamed.cleaned"
    }

    plot_tb_mos_id_vd(
        test_names,
        f"id-vd curves sg13g2_lv_nmos_psp ng=1",
        fig_dir
    )


def plot_inv_chain(
        test_names: dict[str, str],
        title: str,
        fig_name: str,
        show: bool = False
    ):

    test_keys = list(test_names.keys())
    filepaths = [ref_dir / (test_name + '.sp.out') for test_name in test_names.values()]
    data_list = [pd.read_csv(filepath, sep=r'\s+') for filepath in filepaths]

    key_ref = test_keys.pop(0)
    data_ref = data_list.pop(0)
    test_name = list(test_names.values())[0]

    # Extract time and voltage columns from reference
    time_ref = data_ref.iloc[:, 0].values
    voltage_ref = data_ref.iloc[:, 2].values

    fig = plt.figure(figsize=(6 * len(data_list), 8))
    gs = plt.GridSpec(2, len(data_list), bottom=0.2, left=0.2, hspace=0.3)

    for i, data in enumerate(data_list):

        ax0 = plt.subplot(gs[0, i])
        ax1 = plt.subplot(gs[1, i], sharex=ax0)
        ax0.set_title(test_keys[i], fontsize=14)

        # Extract time and voltage from test data
        time_i = data.iloc[:, 0].values
        voltage_i = data.iloc[:, 2].values

        # Verify time arrays match
        assert np.allclose(time_ref, time_i), "Time arrays do not match"

        # Plot overlay: reference (dashed black) and test (solid color)
        ax0.plot(time_i, voltage_i, c='blue', ls='-', lw=2.0, label=test_keys[i])
        ax0.plot(time_ref, voltage_ref, c="orange", ls='--', lw=1.0, label=key_ref)

        # Calculate relative errors
        rel_err_arr = pointwise_rel_err(voltage_ref, voltage_i)

        # Plot errors (use semilogy if errors are non-zero)
        if np.allclose(rel_err_arr, np.zeros_like(rel_err_arr)):
            ax1.plot(time_i, rel_err_arr, c='C0', ls='-')
        else:
            ax1.semilogy(time_i, rel_err_arr, c='C0', ls='-')

        ax0.legend()
        ax0.set_ylabel('Voltage [V]', fontsize=14)
        ax1.set_ylabel(r'$\varepsilon_{\mathrm{rel}}$', fontsize=18)
        ax1.set_xlabel('Time [s]', fontsize=14)

    plt.suptitle(title, fontsize=14)
    fig.align_ylabels()

    plt.savefig(fig_dir / (fig_name + '.png'), dpi=300)

    if show:
        plt.show()

    plt.close()

    return


def plot_tb_moslv_inv_chain_generic_vs_dump(N: int = 10):

    test_names = {
        "generic": f"tb_moslv_inv_chain_N{N}_tt",
        "dump": f"tb_moslv_inv_chain_N{N}_tt.dump",
    }

    title = f"inverter chain N={N}"

    plot_inv_chain(
        test_names,
        title,
        "tb_moslv_inv_chain_N10_generic_vs_dump",
        show=True
    )

def plot_tb_moslv_inv_chain_dump_vs_renamed(N: int = 10):

    test_names = {
        "dump": f"tb_moslv_inv_chain_N{N}_tt.dump",
        "dump.renamed": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed",
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(
        test_names,
        title,
        f"tb_moslv_inv_chain_N{N}_dump_vs_rename",
    )


def plot_tb_moslv_inv_chain_dump_vs_pruned(N: int = 10):

    test_names = {
        "dump": f"tb_moslv_inv_chain_N{N}_tt.dump",
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(
        test_names,
        title,
        f"tb_moslv_inv_chain_N{N}_dump_vs_pruned",
    )

def plot_tb_moslv_inv_chain_pruned_vs_renamed_pruned(N: int = 10):

    test_names = {
        "dump": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.pruned",
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(
        test_names,
        title,
        f"tb_moslv_inv_chain_N{N}_pruned_vs_renamed_pruned",
    )


def plot_tb_moslv_inv_chain_dump_vs_renamed_pruned(N: int = 10):

    test_names = {
        "dump": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.pruned",
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(
        test_names,
        title,
        f"tb_moslv_inv_chain_N{N}_dump.pruned_vs_renamed.pruned"
    )

def plot_tb_moslv_inv_chain_dump_vs_renamed_cleaned(N: int = 10):

    test_names = {
        "dump": f"tb_moslv_inv_chain_N{N}_tt.dump",
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.cleaned",
    }

    title = f"inverter chain N={N}"
    fig_name = f"tb_moslv_inv_chain_N{N}_dump_vs_renamed.cleaned"

    plot_inv_chain(test_names, title, fig_name)

def plot_tb_moslv_inv_chain_pruned_vs_renamed_cleaned_pruned(N: int = 10):

    test_names = {
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
        "dump.renamed.cleaned.pruned.": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.cleaned.pruned",
    }

    title = f"inverter chain N={N}"
    fig_name = f"tb_moslv_inv_chain_N{N}_pruned_vs_renamed.cleaned.pruned"

    plot_inv_chain(test_names, title, fig_name)

def plot_tb_moslv_inv_chain_renamed_cleaned_pruned_vs_renamed_cleaned_pruned_optimized(N: int = 10):

    test_names = {
        "baseline.": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.cleaned.pruned",
        "optimized.": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.cleaned.pruned.optimized",

    }

    title = f"inverter chain N={N}"
    fig_name = f"tb_moslv_inv_chain_N{N}_baseline_vs_optimized"

    plot_inv_chain(test_names, title, fig_name)

def plot_tb_moslv_inv_chain(N: int = 10):

    test_names = {
        "generic": f"tb_moslv_inv_chain_N{N}_tt",
        "dump.cleaned": f"tb_moslv_inv_chain_N{N}_tt.dump.cleaned",
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
        "dump.renamed": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed",
        # "dump.pruneplod.renamed.cleaned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned.renamed.cleaned"
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(test_names, title)

def plot_tb_moslv_inv_chain_trafos(N: int = 10):

    test_names = {
        "dump.cleaned": f"tb_moslv_inv_chain_N{N}_tt.dump.cleaned",
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
        "dump.renamed": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed",
        # "dump.pruneplod.renamed.cleaned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned.renamed.cleaned"
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(test_names, title)

def plot_tb_moslv_inv_chain_trafos(N: int = 10):

    test_names = {
        "dump.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.pruned",
        "dump.renamed.cleaned.pruned": f"tb_moslv_inv_chain_N{N}_tt.dump.renamed.cleaned.pruned",
    }

    title = f"inverter chain N={N}"
    plot_inv_chain(test_names, title)


if __name__ == '__main__':

    # plot_tb_moslv_inv_chain_generic_vs_dump()
    # plot_tb_moslv_inv_chain_dump_vs_renamed()
    # plot_tb_moslv_inv_chain_dump_vs_renamed_pruned()
    # plot_tb_moslv_inv_chain_dump_vs_renamed_cleaned()

    # plot_tb_moslv_inv_chain_pruned_vs_renamed_cleaned_pruned()
    plot_tb_moslv_inv_chain_renamed_cleaned_pruned_vs_renamed_cleaned_pruned_optimized()

    # plot_tb_pmos_id_vd_ng()
    # plot_tb_moslv_inv_chain()
    # plot_tb_moslv_inv_chain_trafos()
