clear
load medicoes/d20_direita_7.vna -mat

x = "ola"
f = SLm.fdxvec;
f = transpose(f);
FRF_acelerometro = SLm.xcmeas(5).xfer;
FRF_vibrometro = SLm.xcmeas(9).xfer;

save('N7_direita_20','f','FRF_acelerometro','FRF_vibrometro')



