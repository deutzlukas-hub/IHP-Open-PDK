#!/usr/bin/env bash

# dump paramset
#gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_paramset_tt.dump.va --dump sg13g2_moslv_paramset_tt.va
# dump multiplier taylored
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_paramset_tt_mult.dump.va --dump sg13g2_moslv_paramset_tt_mult.va
