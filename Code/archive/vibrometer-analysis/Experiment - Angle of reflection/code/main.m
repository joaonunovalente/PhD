%------------------------------------------------------------------------
% João Nuno Valente
% DEM, UA
%------------------------------------------------------------------------
clear; close all; clc;
%------------------------------------------------------------------------
% Load data
%------------------------------------------------------------------------
S = load("../data/data.mat").data;
f = linspace(0, 5000, 3201);   % Frequency vector
omega = 2 * pi * f(:);         % Angular frequency (column)

%------------------------------------------------------------------------
% Extract FRFs
%------------------------------------------------------------------------
NOrthogonal = S.N1.FRF_vibrometer;  % Reference orthogonal measurement

N2 = S.N2.FRF_vibrometer;  % +45°
N3 = S.N3.FRF_vibrometer;  % -45°
N4 = S.N4.FRF_vibrometer;  % +30°
N6 = S.N6.FRF_vibrometer;  % -30°
N5 = S.N5.FRF_vibrometer;  % +20°
N7 = S.N7.FRF_vibrometer;  % -20°

%------------------------------------------------------------------------
% Correct each individual measurement for projection
%------------------------------------------------------------------------
N2_corr = N2 / cosd(45);
N3_corr = N3 / cosd(45);
N4_corr = N4 / cosd(30);
N6_corr = N6 / cosd(30);
N5_corr = N5 / cosd(20);
N7_corr = N7 / cosd(20);

%------------------------------------------------------------------------
% Average z components
%------------------------------------------------------------------------
z1 = (N2_corr + N3_corr) / 2;
z2 = (N4_corr + N6_corr) / 2;
z3 = (N5_corr + N7_corr) / 2;

z_avg = (z1 + z2 + z3) / 3;

%------------------------------------------------------------------------
% Visualize data
%------------------------------------------------------------------------
% Reconstructed Longitudinal Component and Orthogonal Reference
fig1 = figure('WindowState','maximized');
semilogy(f, abs(NOrthogonal), '-.k', 'DisplayName', 'Orthogonal Reference');
hold on;
semilogy(f, abs(z_avg), 'b', 'DisplayName', 'Average Estimate');
legend('Location', 'best');
xlabel('Frequency [Hz]');
ylabel('Magnitude');
title('Comparison of Reconstructed Longitudinal Component and Orthogonal Reference');
grid on;

% Individual Pair Reconstructions
fig2 = figure('WindowState','maximized');
semilogy(f, abs(z_avg), '-.k', 'LineWidth', 1, 'DisplayName', 'Average Estimate');
hold on;
semilogy(f, abs(z1), 'DisplayName', 'Angle 45º');
semilogy(f, abs(z2), 'DisplayName', 'Angle 30º');
semilogy(f, abs(z3), 'DisplayName', 'Angle 20º');
legend('Location', 'best');
xlabel('Frequency [Hz]');
ylabel('Magnitude');
title('Individual Pair Reconstructions');
grid on;

% Error relative to orthogonal measurement
fig3 = figure('WindowState','maximized');
error_avg = 20 * log10(abs(z_avg ./ NOrthogonal));
plot(f, error_avg, 'b', 'DisplayName', 'Average Error [dB]');
xlabel('Frequency [Hz]');
ylabel('Relative Error [dB]');
legend('Location', 'best');
title('Relative Error');
grid on;

%------------------------------------------------------------------------
% Save results (optional)
%------------------------------------------------------------------------
saveas(fig1, '../results/Orthogonal_vs_Estimates_Magnitude.jpg');
saveas(fig2, '../results/Angle_Pairs_Magnitude.jpg');
saveas(fig3, '../results/Relative_Error.jpg');
