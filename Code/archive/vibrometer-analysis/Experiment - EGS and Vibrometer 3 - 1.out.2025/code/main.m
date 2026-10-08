%% Minimal FRF comparison: orthogonal, angled, geometric projection
close all; clear; clc;

dataFolder = "../data/";
file_ref  = fullfile(dataFolder, "measurement_1.1.mat");  
file_angle = fullfile(dataFolder, "measurement_9.1.mat"); 
theta_deg = 47.9;  

% --- Load reference ---
refData = load(file_ref);
H_ref = refData.vibrometer.FRF.y_values.values / 5;
freq_ref = transpose((refData.vibrometer.FRF.x_values.start_value:...
    refData.vibrometer.FRF.x_values.number_of_values-1) * ...
    refData.vibrometer.FRF.x_values.increment);
omega_ref = 2*pi*freq_ref;
H_ref = 1i*omega_ref.*H_ref;

% --- Load angled ---
angData = load(file_angle);
H_ang = angData.vibrometer.FRF.y_values.values / 5;
freq_ang = transpose((angData.vibrometer.FRF.x_values.start_value:...
    angData.vibrometer.FRF.x_values.number_of_values-1) * ...
    angData.vibrometer.FRF.x_values.increment);
omega_ang = 2*pi*freq_ang;
H_ang = 1i*omega_ang.*H_ang;

% --- Align frequency grids ---
f_min = max(min(freq_ref), min(freq_ang));
f_max = min(max(freq_ref), max(freq_ang));
Ncommon = min(length(freq_ref), length(freq_ang));
freq = linspace(f_min, f_max, Ncommon).';
H_ref = interp1(freq_ref, H_ref, freq, 'pchip');
H_ang = interp1(freq_ang, H_ang, freq, 'pchip');

% --- Geometric reconstruction ---
theta = deg2rad(theta_deg);
H_geom = H_ang / cos(theta);

% --- Plots ---
figure('Color','w');
% subplot(2,1,1);
semilogy(freq(100:end-150), abs(H_ref(100:end-150)),'k','LineWidth',1); hold on;
semilogy(freq(100:end-150), abs(H_ang(100:end-150)),'b:','LineWidth',1);
semilogy(freq(100:end-150), abs(H_geom(100:end-150)),'r--','LineWidth',1);
xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
legend('Orthogonal (0º)','Angled (42.5º)','Geometric Projection'); grid on;
title('FRF Magnitudes: Orthogonal vs Measurement 9 (42.5º)');

figure('Color','w');
% subplot(2,1,2);
plot(freq, 20*log10(abs(H_ref)./abs(H_ang)),'b:'); hold on;
plot(freq, 20*log10(abs(H_ref)./abs(H_geom)),'r--');
xlabel('Frequency (Hz)'); ylabel('Δ|H| (dB)');
legend('Angled','Geom'); grid on;
title('Magnitude difference (Ref / Test)');
