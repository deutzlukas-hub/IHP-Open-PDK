#!/usr/bin/env python3
"""
Generate inverter chain testbench for ngspice
"""

def generate_inverter_chain(
    num_inverters=5,
    corner='tt',
    osdi_model='sg13g2_moslv_paramset_openvaf_nolocalparam_instance.osdi',
    output_file=None,
    w_nmos=0.35e-6,
    w_pmos=0.28e-6,
    l_nmos=0.34e-6,
    l_pmos=0.34e-6,
    vdd=1.2,
    load_cap=10e-15,
    tran_time=100e-9,
    tran_step=0.1e-9
):

    if output_file is None:
        output_file = f"tb_moslv_inv_chain_N{num_inverters}_{corner}.sp"

    # Generate netlist content
    lines = []
    lines.append(f"* CMOS inverter chain with {num_inverters} stages")
    lines.append(f"* Corner: {corner}")
    lines.append("")
    lines.append("* bind osdi to spice model")
    lines.append(".model sg13_lv_nmos_test sg13g2_lv_nmos_psp")
    lines.append(".model sg13_lv_pmos_test sg13g2_lv_pmos_psp")
    lines.append("")
    lines.append(".option reltol=1e-4")
    lines.append("")
    lines.append(f"VDD vdd 0 {vdd}")
    lines.append(f"VIN in 0 PWL(0 0 10n 0 11n {vdd} {tran_time*1e9}n {vdd})")
    lines.append("")
    lines.append("* Inverter subcircuit")
    lines.append(".subckt inv in out vdd gnd")
    lines.append(f"X1 out in vdd vdd sg13_lv_pmos w={w_pmos} l={l_pmos} rfmode=0")
    lines.append(f"X2 out in gnd gnd sg13_lv_nmos w={w_nmos} l={l_nmos} rfmode=0")
    lines.append(".ends")
    lines.append("")
    lines.append("* Inverter chain instances")

    for i in range(1, num_inverters + 1):
        if i == 1:
            in_node = "in"
        else:
            in_node = f"n{i-1}"

        if i == num_inverters:
            out_node = "out"
        else:
            out_node = f"n{i}"

        lines.append(f"X{i} {in_node} {out_node} vdd 0 inv")

    lines.append("")
    lines.append("* Load capacitance")
    lines.append(f"CL out 0 {load_cap}")
    lines.append("")
    lines.append(".control")
    lines.append(f"pre_osdi {osdi_model}")
    lines.append("set wr_vecnames")
    lines.append("set wr_singlescale")
    lines.append(f"tran {tran_step} {tran_time}")
    lines.append(f"wrdata check/{output_file}.out v(in) v(out) i(VDD)")
    lines.append(".endc")
    lines.append(".end")
    lines.append("")

    # Write to file
    netlist_content = "\n".join(lines)
    with open(output_file, 'w') as f:
        f.write(netlist_content)

    print(f"Generated {output_file} with {num_inverters} inverter stages")

    return output_file

if __name__ == "__main__":
    generate_inverter_chain(num_inverters=10)
    # generate_inverter_chain(num_inverters=50)
    # generate_inverter_chain(num_inverters=100)
    # generate_inverter_chain(num_inverters=500)
    # generate_inverter_chain(num_inverters=1000)

