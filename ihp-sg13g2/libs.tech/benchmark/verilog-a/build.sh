#!/usr/bin/env bash
set -euo pipefail

# build from generic
openvaf-r ../psp103/psp103.va ../osdi/psp103.osdi
# build from paramset
openvaf-r sg13g2_moslv_paramset_tt_nolocal.dump.va -o ../osdi/sg13g2_moslv.osdi
# build from tayolored paramset
openvaf-r sg13g2_moslv_paramset_tt_mult_nolocal.dump.va -o ../osdi/sg13g2_moslv_mult.osdi
