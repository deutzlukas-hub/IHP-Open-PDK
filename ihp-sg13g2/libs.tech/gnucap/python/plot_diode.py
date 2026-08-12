from io import StringIO

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dirs import tests_dir_gc, tests_dir_sp, fig_dir
from parse import split_nested_sweep, filter_data
from util import pointwise_rel_err

diode_fig_dir = fig_dir / "diode"
diode_fig_dir.mkdir(parents=True, exist_ok=True)

ref_dir_gc = tests_dir_gc / "diode" / "ref"
ref_dir_sp = tests_dir_sp / "diode" / "ref"
assert ref_dir_gc.exists()
assert ref_dir_sp.exists()

def plot_test_dio_antenna_dc(show: bool = False) -> None:

    test_name = f"test_dio_antenna_dc"

    filepath_gc = ref_dir_gc / (test_name + ".gc.out")
    filepath_sp = ref_dir_sp / (test_name + ".sp.out")

    data_gc_str = filter_data(filepath_gc, ("parameter"))
    data_gc = pd.read_csv(StringIO(data_gc_str), sep=r"\s+", skipfooter=5, engine="python").values
    data_sp = pd.read_csv(filepath_sp, sep=r"\s+", engine="python").values

    v_gc = data_gc[:, 0]
    i1_gc = np.abs(data_gc[:, 1]) * 1e6
    i2_gc = np.abs(data_gc[:, 2]) * 1e6

    v_sp = data_sp[:, 0]
    i1_sp = np.abs(data_sp[:, 1]) * 1e6
    i2_sp = np.abs(data_sp[:, 2]) * 1e6

    fig = plt.figure(figsize=(10, 10))
    gs = plt.GridSpec(2, 2, hspace=0.2, wspace=0.3)
    ax0 = plt.subplot(gs[0])
    ax00 = plt.subplot(gs[0, 0], sharex=ax0)
    ax10 = plt.subplot(gs[1, 0], sharex=ax0)
    ax01 = plt.subplot(gs[0, 1], sharex=ax0)
    ax11 = plt.subplot(gs[1, 1], sharex=ax0)


    ax00.set_title("I-V dantenna", fontsize=16)
    ax01.set_title("I-V dpantenna", fontsize=16)

    ax00.plot(v_gc, i1_gc, "-", color="b", linewidth=2, label="Gnucap")
    ax00.plot(v_sp, i1_sp, "--", color="k", linewidth=1.5, label="ngspice")
    ax00.set_ylabel(r"I [$\mu$A]", fontsize=12)
    ax00.set_xlabel("Bias voltage [V]", fontsize=12)
    ax00.grid(True, alpha=0.3)
    ax00.legend()

    rel_abs_err_vmda = pointwise_rel_err(i1_gc, i1_sp)
    ax10.semilogy(v_gc, rel_abs_err_vmda, "-", color="b", linewidth=1.0)
    ax10.set_xlabel("Bias voltage [V]", fontsize=12)
    ax10.set_ylabel(r"$\varepsilon_{\mathrm{rel}}$", fontsize=12)
    ax10.grid(True, alpha=0.3)

    ax01.plot(v_gc, i2_gc, "-", color="r", linewidth=2, label="Gnucap")
    ax01.plot(v_sp, i2_sp, "--", color="k", linewidth=1.5, label="ngspice")
    ax01.set_ylabel(r"I [$\mu$A]", fontsize=12)
    ax01.set_xlabel("Bias voltage [V]", fontsize=12)
    ax01.grid(True, alpha=0.3)
    ax01.legend()

    rel_abs_err_vmda = pointwise_rel_err(i1_gc, i1_sp)
    ax11.semilogy(v_gc, rel_abs_err_vmda, "-", color="r", linewidth=1.0)
    ax11.set_xlabel("Bias voltage [V]", fontsize=12)
    ax11.set_ylabel(r"$\varepsilon_{\mathrm{rel}}$", fontsize=12)
    ax11.grid(True, alpha=0.3)

    plt.savefig(diode_fig_dir / (test_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()

def plot_test_dio_antenna_temp(show: bool = False) -> None:

    test_name = f"test_dio_antenna_temp"

    filepath_gc = ref_dir_gc / (test_name + ".gc.out")
    filepath_sp = ref_dir_sp / (test_name + ".sp.out")

    data_gc_str = filter_data(filepath_gc, ("parameter"))
    data_gc = pd.read_csv(StringIO(data_gc_str), sep=r"\s+", skipfooter=5, engine="python").values
    data_sp = pd.read_csv(filepath_sp, sep=r"\s+", engine="python").values

    # v1 = dantenna, v2 = dpantenna
    
    temp_gc = data_gc[:, 0]
    v1_gc = data_gc[:, 1]
    v2_gc = data_gc[:, 2]

    temp_sp = data_sp[:, 0]
    v1_sp = data_sp[:, 1]
    v2_sp = data_sp[:, 2]

    assert(np.allclose(temp_gc, temp_sp))

    fig = plt.figure(figsize=(10, 8))

    gs = plt.GridSpec(2, 2, hspace=0.3, wspace=0.3)
    ax00 = plt.subplot(gs[0, 0])
    ax01 = plt.subplot(gs[0, 1])
    ax10 = plt.subplot(gs[1, 0])
    ax11 = plt.subplot(gs[1, 1])

    plt.suptitle(f"V vs Temperature: dantenna and dpantenna", fontsize=14,)

    ax00.plot(temp_gc, v1_gc, "-", color="r", linewidth=2, label="Gnucap V(Vd)")
    ax00.plot(temp_sp, v1_sp, "--", color="k", linewidth=1.5, label="Ngspice V(Vd)")
    ax00.set_ylabel("V [V]", fontsize=12)
    ax00.grid(True, alpha=0.3)
    ax00.legend()

    rel_error_v1 = np.abs((v1_gc - v1_sp) / v1_gc)

    ax01.semilogy(temp_gc, rel_error_v1, "-", color="b", linewidth=1.5)
    ax01.set_ylabel(r"$\varepsilon_\mathrm{rel}$ V(Vd)", fontsize=12)
    ax01.set_xlabel("Temperature [°C]", fontsize=12)
    ax01.grid(True, alpha=0.3)

    ax10.plot(temp_gc, v2_gc, "-", color="r", linewidth=2, label="Gnucap V(Vdp)")
    ax10.plot(temp_sp, v2_sp, "--", color="k", linewidth=1.5, label="Ngspice V(Vdp)")
    ax10.set_ylabel("V(Vdp) [V]", fontsize=12)
    ax10.grid(True, alpha=0.3)
    ax10.legend()

    rel_error_v2 = np.abs((v2_gc - v2_sp) / v2_gc)
    ax11.semilogy(temp_gc, rel_error_v2, "-", color="b", linewidth=1.5)
    ax11.set_ylabel(r"$\varepsilon_\mathrm{rel}$ V(Vdp)", fontsize=12)
    ax11.set_xlabel("Temperature [°C]", fontsize=12)
    ax11.grid(True, alpha=0.3)

    plt.savefig(diode_fig_dir / (test_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()

def plot_test_dc_isolbox(corner: str = "typ", show: bool = False) -> None:

    test_name = f"test_dc_isolbox_{corner}"

    filepath_gc = ref_dir_gc / (test_name + ".gc.out")
    filepath_sp = ref_dir_sp / "tb_dio_isolbox.sp.out"

    data_gc = pd.read_csv(
        filepath_gc, sep=r"\s+", skipfooter=4, engine="python"
    ).values
    data_sp = pd.read_csv(filepath_sp, sep=r"\s+", engine="python").values

    ibias_gc = data_gc[:, 2]
    viso_gc = data_gc[:, 0]
    vn_gc = data_gc[:, 1]

    ibias_sp = data_sp[:, 0]
    viso_sp = data_sp[:, 1]

    fig = plt.figure(figsize=(10, 8))
    gs = plt.GridSpec(2, 1, hspace=0.3)
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)

    plt.suptitle(
        f"isolbox breakdown DC sweep ({corner.upper()} Corner)",
        fontsize=14,
    )

    ax0.plot(ibias_gc, viso_gc, "-", color="r", linewidth=2, label="Gnucap v(isosub_net)")
    ax0.plot(ibias_sp, viso_sp, "--", color="k", linewidth=1.5, label="Ngspice v(isosub_net)")
    ax0.set_ylabel("V(isosub_net) [V]", fontsize=12)
    ax0.grid(True, alpha=0.3)
    ax0.legend()

    ax1.plot(ibias_gc, vn_gc, "-", color="b", linewidth=2, label="Gnucap v(nwell_net) [floating]")
    ax1.axhline(0, color="grey", linestyle=":", linewidth=1.0)
    ax1.set_xlabel("I(bias) [A]", fontsize=12)
    ax1.set_ylabel("V(nwell_net) [V]", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    plt.savefig(diode_fig_dir / (test_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_test_dio_isolbox_dc(show: bool = False) -> None:

    test_name = f"test_dio_isolbox_dc"

    filepath_gc = ref_dir_gc / (test_name + ".gc.out")
    filepath_sp = ref_dir_sp / (test_name + ".sp.out")

    data_gc_str = filter_data(filepath_gc, ("parameter", "open circuit", "#"))
    data_gc = pd.read_csv(
        StringIO(data_gc_str), sep=r"\s+", skipfooter=5, header=None, engine="python"
    ).values
    data_sp = pd.read_csv(filepath_sp, sep=r"\s+", engine="python").values

    ibias_gc = data_gc[:, 0]
    viso_gc = data_gc[:, 1]

    ibias_sp = data_sp[:, 0]
    viso_sp = data_sp[:, 1]

    assert(np.allclose(ibias_gc, ibias_sp))

    fig = plt.figure(figsize=(10, 8))
    gs = plt.GridSpec(2, 1, hspace=0.3)
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)

    plt.suptitle(
        f"isolbox breakdown DC I-V sweep",
        fontsize=14,
    )

    ax0.plot(ibias_gc, viso_gc, "-", color="r", linewidth=2, label="Gnucap")
    ax0.plot(ibias_sp, viso_sp, "--", color="k", linewidth=1.5, label="Ngspice")
    ax0.set_ylabel("V(isosub_net) [V]", fontsize=12)
    ax0.grid(True, alpha=0.3)
    ax0.legend()

    rel_abs_err = pointwise_rel_err(viso_sp, viso_gc)
    ax1.semilogy(ibias_gc, rel_abs_err, "-", color="k", linewidth=1.0)
    ax1.set_xlabel("I(bias) [A]", fontsize=12)
    ax1.set_ylabel(r"$\varepsilon_{\mathrm{rel}}$", fontsize=14)
    ax1.grid(True, alpha=0.3)

    plt.savefig(diode_fig_dir / (test_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_test_dio_schottky_dc(show: bool = False) -> None:

    test_name = f"test_dio_schottky_dc"

    filepath_gc = ref_dir_gc / (test_name + ".gc.out")
    filepath_sp = ref_dir_sp / (test_name + ".sp.out")

    data_gc_str = filter_data(filepath_gc,
        ("#", "parameter", "tb.", "did not converge", "Gnucap", "iterations:", "transient", "nodes:", "dctran"),
    )

    data_gc = pd.read_csv(StringIO(data_gc_str), sep=r"\s+", header=None, engine="python").dropna().values.astype(float)
    data_sp = pd.read_csv(filepath_sp, sep=r"\s+", engine="python").values

    is_gc = data_gc[:, 0] * 1e3
    vd_gc = data_gc[:, 1]

    is_sp = data_sp[:, 0] * 1e3
    vd_sp = data_sp[:, 1]

    assert np.allclose(is_gc, is_sp)

    fig = plt.figure(figsize=(10, 8))
    gs = plt.GridSpec(2, 1, hspace=0.3)
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)

    plt.suptitle(f"schottky_nbl1 DC V-I sweep", fontsize=14)

    ax0.plot(is_gc, vd_gc, "-",  color="r", linewidth=3, label="Gnucap")
    ax0.plot(is_sp, vd_sp, "--", color="k", linewidth=1.5, label="ngspice")
    ax0.set_ylabel("Diode voltage $V_D$ [V]", fontsize=12)
    ax0.grid(True, alpha=0.3)
    ax0.legend()


    rel_abs_err = pointwise_rel_err(vd_sp, vd_gc, 1e-2)
    ax1.semilogy(is_gc, rel_abs_err, "-", color="red", linewidth=1.0)
    ax1.set_xlabel("Source current I [mA]", fontsize=12)
    ax1.set_ylabel(r"$\varepsilon_{\mathrm{rel}}$", fontsize=14)
    ax1.grid(True, alpha=0.3)

    plt.savefig(diode_fig_dir / (test_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_test_isolbox_sweep(corner: str = "typ", show: bool = False) -> None:

    test_name = f"test_isolbox_sweep_{corner}"

    filepath_gc = ref_dir_gc / (test_name + ".gc.out")
    filepath_sp = ref_dir_sp / "tb_dio_isolbox_sweep.sp.out"

    data_gc = pd.read_csv(filepath_gc, sep=r"\s+", skipfooter=4, engine="python").values
    data_sp = pd.read_csv(filepath_sp, sep=r"\s+", engine="python").values

    iso_l_gc_unique, _, iso_w_gc_unique = split_nested_sweep(data_gc, [0, 1], inner_sweep_col_idx=2, outer_sweep_col_idx=3)

    idx_sp = data_sp[:, 0]
    vbk_pos_sp = data_sp[:, 1]
    vbk_neg_sp = data_sp[:, 2]

    igc = iso_l_gc_unique
    vbk_pos_gc = np.zeros_like(igc)
    vbk_neg_gc = np.zeros_like(igc)

    for j in range(len(igc)):
        v_iso_at_pos = iso_l_gc_unique[j]
        v_g = iso_w_gc_unique[j]
        v_g = np.asarray(v_g)
        if v_g.size == 0 or v_iso_at_pos.size == 0:
            continue
        idx_pos = int(np.argmin(np.abs(v_g - 1e-6)))
        idx_neg = int(np.argmin(np.abs(v_g + 1e-6)))
        vbk_pos_gc[j] = v_iso_at_pos[idx_pos]
        vbk_neg_gc[j] = v_iso_at_pos[idx_neg]

    fig = plt.figure(figsize=(10, 10))

    gs = plt.GridSpec(2, 1, hspace=0.3)
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)

    plt.suptitle(f"isolbox breakdown voltage vs iso_l ({corner.upper()} Corner)", fontsize=14)

    ax0.plot(igc, vbk_pos_gc, "-o", color="r", linewidth=2, label="Gnucap vbk_pos")
    ax0.plot(idx_sp, vbk_pos_sp, "--s", color="k", linewidth=1.5, label="Ngspice vbk_pos")
    ax0.set_ylabel("vbk_pos [V]", fontsize=12)
    ax0.grid(True, alpha=0.3)
    ax0.legend()

    ax1.plot(igc, vbk_neg_gc, "-o", color="b", linewidth=2, label="Gnucap vbk_neg")
    ax1.plot(idx_sp, vbk_neg_sp, "--s", color="k", linewidth=1.5, label="Ngspice vbk_neg")
    ax1.set_xlabel("iso_l index / idx_vec", fontsize=12)
    ax1.set_ylabel("vbk_neg [V]", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    plt.savefig(diode_fig_dir / (test_name + ".png"), dpi=300)

    if show:
        plt.show()

    plt.close()


def main() -> None:

    plot_test_dio_antenna_dc()
    plot_test_dio_antenna_temp()
    plot_test_dio_isolbox_dc()
    plot_test_dio_schottky_dc()

    # plot_test_dio_esd_diodes()

    print("Finished plotting diode!")


if __name__ == "__main__":

    main()
