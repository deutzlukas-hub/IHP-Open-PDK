#!/usr/bin/env bash


# dump all purpose paramset
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_paramset_tt.dump.va --dump sg13g2_moslv_paramset_tt.va

# dump tailored inv_chain paramset
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_paramset_tt_inv_chain.dump.va --dump sg13g2_moslv_paramset_tt_inv_chain.va

