close all; clear; clc;

dataFolder = "../data/";
file_vib  = fullfile(dataFolder, "acc.mat");
data = load(file_vib);

% Load accelerometer data
H_acc_x = data.accelerometer_x.FRF.y_values.values;
H_acc_y = data.accelerometer_y.FRF.y_values.values;
H_acc_z = data.accelerometer_z.FRF.y_values.values;

% Compute frequency

file_vib  = fullfile(dataFolder, "vib6.mat");
data = load(file_vib);

freq_inc1 = data.vib.FRF.x_values.increment;
num_vals1 = data.vib.FRF.x_values.number_of_values;
start_val1 = data.vib.FRF.x_values.start_value;
freq = transpose((start_val1:num_vals1-1) * freq_inc1);

% Load Vibrometer
angle = 0;
refData = load(file_vib);
H_ref = refData.vib.FRF.y_values.values / 5;   % velocity/forces
omega_ref = 2*pi*freq;
H_ref = 1i .* omega_ref .* H_ref;
H_ref_correted = H_ref / cosd(angle);


% --- Plots ---
figure('Color','w');
semilogy(freq(100:end-150), abs(H_acc_x(100:end-150)),'b','LineWidth',0.7); hold on;
semilogy(freq(100:end-150), abs(H_acc_y(100:end-150)),'k:','LineWidth',1); hold on;
semilogy(freq(100:end-150), abs(H_acc_z(100:end-150)),'r--','LineWidth',1);

% semilogy(freq(100:end-150), abs(H_ref(100:end-150)),'k--','LineWidth',1);
semilogy(freq(100:end-150), abs(H_ref_correted(100:end-150)),'g','LineWidth',1);

xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
legend('Accelerometer X','Accelerometer Y','Acceleeromter Z', 'Vibrometer'); grid on;

% legend('Accelerometer Y','Vibrometer', 'Vibrometer corrected (45º)'); grid on;
title('Measurment');
