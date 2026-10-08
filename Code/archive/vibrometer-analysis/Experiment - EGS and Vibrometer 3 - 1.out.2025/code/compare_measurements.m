close all; clear; clc;

%% --- PARAMETERS ---
dataFolder = "../data/";
file = fullfile(dataFolder, "measurement_1.1.mat");

%% --- STEP 1: Load accelerometer data ---
accData = load(file);
accel_FRF_mag = abs(accData.accelerometer_z.FRF.y_values.values);
freq_inc_a = accData.accelerometer_z.FRF.x_values.increment;
num_vals_a = accData.accelerometer_z.FRF.x_values.number_of_values;
start_val_a = accData.accelerometer_z.FRF.x_values.start_value;
freq_acc = transpose((start_val_a:num_vals_a-1) * freq_inc_a);

%% --- STEP 2: Load selected vibrometer measurement ---
vibData = load(file);

vib = vibData.vibrometer.FRF.y_values.values / 5;
freq_inc_v = vibData.vibrometer.FRF.x_values.increment;
num_vals_v = vibData.vibrometer.FRF.x_values.number_of_values;
start_val_v = vibData.vibrometer.FRF.x_values.start_value;
freq_vib = transpose((start_val_v:num_vals_v-1) * freq_inc_v);

% Convert velocity to acceleration
omega = 2 * pi * freq_vib;
accel_vib = zeros(size(vib));
nz = (freq_vib ~= 0);
accel_vib(nz) = 1i * omega(nz) .* vib(nz);
accel_vib_mag = abs(accel_vib);

%% --- STEP 3: Plot comparison ---
figure;
semilogy(freq_vib, accel_vib_mag, 'b', 'LineWidth', 1); hold on;
semilogy(freq_acc, accel_FRF_mag, 'r', 'LineWidth', 1);
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title(['Accelerometer vs. Vibrometer' ["Measurement " + file{1}(21)]]);
legend('Vibrometer', 'Accelerometer', 'Location', 'best');
grid on;
set(gca, 'YScale', 'log');
