clear; close all; clc
load 1.vna -mat

f = transpose(SLm.fdxvec);

% Extract non-empty FRFs
FRF_x = SLm.xcmeas(5).xfer;
FRF_y = SLm.xcmeas(9).xfer;
FRF_z = SLm.xcmeas(13).xfer;

coh_x = SLm.xcmeas(5).coh;
coh_y = SLm.xcmeas(9).coh;
coh_z = SLm.xcmeas(13).coh;

FRF_vibrometer = SLm.scmeas(3).aspec * 10 ^ 8.5;

% Plot
figure(1)
semilogy(f, abs(FRF_vibrometer), 'k', 'LineWidth', 1.5)
hold on
semilogy(f, abs(FRF_x), 'b', 'LineWidth', 1)
semilogy(f, abs(FRF_y), 'r', 'LineWidth', 1)
semilogy(f, abs(FRF_z), 'g', 'LineWidth', 1)
xlabel('Frequency (Hz)')
ylabel('Magnitude')
title('Frequency Response Functions')
legend('Vibrometer','X', 'Y', 'Z')
grid on


figure(2)
plot(f, coh_x, 'b', 'LineWidth', 1.5)
hold on
plot(f, coh_y, 'r', 'LineWidth', 1.5)
plot(f, coh_z, 'g', 'LineWidth', 1.5)
xlabel('Frequency (Hz)')
ylabel('Magnitude')
title('Time Response - Acelerometer')
legend('X', 'Y', 'Z')
% grid on

for i = 1:length(SLm.xcmeas)
    xferData = SLm.xcmeas(i).xfer;
    if isempty(xferData)
        fprintf('xcmeas(%d).fft is EMPTY\n', i);
    else
        fprintf('xcmeas(%d).acor contains data: size = [%s]\n', i, num2str(size(xferData)));
    end
end