from pathlib import Path

base_dir = Path(__file__).resolve().parent

build_dir = base_dir / "build"
check_dir = base_dir / "check"
bm_dir = base_dir / "bm"
ref_dir = base_dir / "ref"
log_dir = base_dir / "log"

build_dir.mkdir(parents=True, exist_ok=True)
check_dir.mkdir(parents=True, exist_ok=True)
bm_dir.mkdir(parents=True, exist_ok=True)
ref_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)

PDK_LIBS_DIR = "$PDK_ROOT/$PDK/libs.tech"





