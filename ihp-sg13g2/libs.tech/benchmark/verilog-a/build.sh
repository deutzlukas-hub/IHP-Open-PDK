#!/usr/bin/env bash
set -euo pipefail


# ------------------------------------------------------------------------------
# psp103 vanilla

# build generic
openvaf-r ./psp103/psp103.va -o ../osdi/psp103.osdi

# build all purpose paramset
openvaf-r sg13g2_moslv_paramset_tt.dump.nolocal.va -o ../osdi/sg13g2_moslv.osdi

# build tailored paramset dump
openvaf-r sg13g2_moslv_paramset_tt_tailored.dump.nolocal.va -o ../osdi/sg13g2_moslv_tailored.osdi

# ------------------------------------------------------------------------------
# psp103 nqs

# build generic
openvaf-r ./psp103/psp103_nqs.va -o ../osdi/psp103_nqs.osdi

# build all purpose paramset

# openvaf-r sg13g2_moslv_rf_paramset_tt.dump.nolocal.va -o ../osdi/sg13g2_moslv_rf.osdi

# build tailored paramset
openvaf-r sg13g2_moslv_rf_paramset_tt_tailored.dump.nolocal.va -o ../osdi/sg13g2_moslv_rf_tailored.osdi


