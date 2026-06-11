from os import mkdir
from pathlib import Path

ngspice_dir = Path(__file__).resolve().parent.parent
assert ngspice_dir.is_dir()

fig_dir = ngspice_dir / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)



