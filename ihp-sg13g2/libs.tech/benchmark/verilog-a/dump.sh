#!/usr/bin/env bash


# psp103 vanilla

# dump psp103 for debugging.
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o psp103.dump.va --dump ./psp103/psp103.va

# dump all purpose paramset
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_paramset_tt.dump.va --dump sg13g2_moslv_paramset_tt.va

# dump tailored paramset
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_paramset_tt_tailored.dump.va --dump sg13g2_moslv_paramset_tt_tailored.va

# psp103_nqs

# dump psp103_nqs for debugging.
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o psp103_nqs.dump.va --dump ./psp103/psp103_nqs.va

# dump all purpose paramset
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_rf_paramset_tt.dump.va --dump sg13g2_moslv_rf_paramset_tt.va

# dump tailored paramset
gnucap-mg-vams -I /usr/local/include/gnucap -I . -I ./psp103 -o sg13g2_moslv_rf_paramset_tt_tailored.dump.va --dump sg13g2_moslv_rf_paramset_tt_tailored.va
