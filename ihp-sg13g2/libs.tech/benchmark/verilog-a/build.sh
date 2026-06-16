#!/usr/bin/env bash
set -euo pipefail

# build from generic
openvaf-r ./psp103/psp103.va -o ../osdi/psp103.osdi
## build dummped generic for debugging
#openvaf-r psp103.dump.va -o ../osdi/psp103_from_dump.osdi
# build from paramset dump
openvaf-r sg13g2_moslv_paramset_tt_nolocal.dump.va -o ../osdi/sg13g2_moslv.osdi
# build from multiplier paramset dump
openvaf-r sg13g2_moslv_paramset_tt_mult_nolocal.dump.va -o ../osdi/sg13g2_moslv_mult.osdi
# build from inv_chain paramset dump
openvaf-r sg13g2_moslv_paramset_tt_inv_chain_nolocal.dump.va -o ../osdi/sg13g2_moslv_inv_chain.osdi

