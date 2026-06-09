from pathlib import Path

benchmark_dir = Path(__file__).resolve().parent.parent

dir_sp = benchmark_dir / "ngspice"
check_dir_sp = dir_sp / "check"
ref_dir_sp = dir_sp / "ref"
bm_dir_sp = dir_sp / "bm"
fig_sp = benchmark_dir / "figures"

assert dir_sp.is_dir()
assert ref_dir_sp.is_dir()
assert check_dir_sp.is_dir()

