%------------------------------------------------------------------------
% João Nuno Valente
% DEM, UA
%------------------------------------------------------------------------
clear; close all; clc;
%------------------------------------------------------------------------
% Load data
%------------------------------------------------------------------------
M1 = load("../data/medida1.mat");
M2 = load("../data/medida2.mat");
M3 = load("../data/medida3.mat");
M4 = load("../data/medida4.mat");
M5 = load("../data/medida5.mat");
M6 = load("../data/medida6.mat");
f = transpose(linspace(0, 5000, 1601));   % Frequency vector
omega = 2 * pi * f(:);         % Angular frequency (column)

%------------------------------------------------------------------------
% Extract FRFs
%------------------------------------------------------------------------
MAcelerometro = M1.FRF_acelerometro ./ omega * 100000;  % 
M1 = M1.FRF_vibrometro;  
M2 = M2.FRF_vibrometro;  
M3 = M3.FRF_vibrometro;   
M4 = M4.FRF_vibrometro;   
M5 = M5.FRF_vibrometro;   
M6 = M6.FRF_vibrometro;   

%------------------------------------------------------------------------
% Correct each individual measurement for projection
%------------------------------------------------------------------------
M1_corr = M1;  
M2_corr = M2;   
M3_corr = M3 / cosd(44.53);
M4_corr = M4 / cosd(22.61);
M5_corr = M5 / cosd(27.69);
M6_corr = M6 / cosd(46.09);

%------------------------------------------------------------------------
% Average z components
%------------------------------------------------------------------------
Z1 = (M3_corr + M4_corr) / 2;
Z2 = (M3_corr + M5_corr) / 2;
Z3 = (M3_corr + M6_corr) / 2;
Z4 = (M4_corr + M5_corr) / 2;
Z5 = (M4_corr + M6_corr) / 2;
Z6 = (M5_corr + M6_corr) / 2;

Z = (M3_corr + M4_corr + M5_corr + M6_corr) / 4;

%------------------------------------------------------------------------
% Visualize data
%------------------------------------------------------------------------
% --- Reconstructed Longitudinal Component and Orthogonal Reference
fig1 = figure('WindowState','maximized');
semilogy(f, abs(M1_corr), '-.k', 'DisplayName', 'Orthogonal Reference');
hold on;
semilogy(f, abs(Z), 'DisplayName', 'M3 + M4 + M5 + M6');

legend('Location', 'best');
xlabel('Frequency [Hz]');
ylabel('Magnitude');
% title('Comparison of Reconstructed Longitudinal Component and Orthogonal Reference');
grid on;

% --- Comparision of Longitudinal Components
fig2 = figure('WindowState','maximized');
semilogy(f, abs(M1), '-.k', 'LineWidth', 2, 'DisplayName', 'Orthogonal Reference');
hold on;
semilogy(f, abs(M3_corr), 'DisplayName', 'M3');
semilogy(f, abs(M4_corr), 'DisplayName', 'M4');
semilogy(f, abs(M5_corr), 'DisplayName', 'M5');
semilogy(f, abs(M6_corr), 'DisplayName', 'M6');

legend('Location', 'best');
xlabel('Frequency [Hz]');
ylabel('Magnitude');
% title('Comparison of Reconstructed Longitudinal Component and Orthogonal Reference');
grid on;

% --- Error relative to orthogonal measurement
fig3 = figure('WindowState','maximized');
plot(f, 20 * log10(abs(Z ./ M1)),'-.k', 'LineWidth', 2, 'DisplayName', 'M3 + M4 + M5 + M6 [dB]');
hold on
plot(f, 20 * log10(abs(Z1 ./ M1)), 'DisplayName', 'M3 + M4 [dB]');
plot(f, 20 * log10(abs(Z2 ./ M1)), 'DisplayName', 'M3 + M5 [dB]');
plot(f, 20 * log10(abs(Z3 ./ M1)), 'DisplayName', 'M3 + M6 [dB]');
plot(f, 20 * log10(abs(Z4 ./ M1)), 'DisplayName', 'M4 + M5 [dB]');
plot(f, 20 * log10(abs(Z5 ./ M1)), 'DisplayName', 'M4 + M6 [dB]');
plot(f, 20 * log10(abs(Z5 ./ M1)), 'DisplayName', 'M5 + M6 [dB]');

xlabel('Frequency [Hz]');
ylabel('Relative Error [dB]');
legend('Location', 'best');
% title('Relative Error');
grid on;

%------------------------------------------------------------------------
% Save results (optional)
%------------------------------------------------------------------------
saveas(fig1, '../results/Orthogonal_vs_Estimate_Magnitude.jpg');
saveas(fig2, '../results/Angle_Pairs_Magnitude.jpg');
saveas(fig3, '../results/Relative_Error.jpg');
