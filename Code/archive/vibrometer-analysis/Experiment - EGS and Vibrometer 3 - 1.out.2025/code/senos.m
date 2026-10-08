close all; clear; clc;

%% --- PARAMETERS ---
dataFolder = "../data/";
file = fullfile(dataFolder, "measurement_14.mat");

%% --- STEP 1: Frequency ---
Data = load(file);
freq_inc_a = Data.accelerometer_z.Time.x_values.increment;
num_vals_a = Data.accelerometer_z.Time.x_values.number_of_values;
start_val_a = Data.accelerometer_z.Time.x_values.start_value;
freq = transpose((start_val_a:num_vals_a-1) * freq_inc_a) * 100 ;

%% --- STEP 2: Load Accelerometer measurements ---

accel_x = abs(Data.accelerometer_x.Time.y_values.values);
accel_y = abs(Data.accelerometer_y.Time.y_values.values);
accel_z = abs(Data.accelerometer_z.Time.y_values.values);



%% --- STEP 2: Load selected vibrometer measurement ---
vib = Data.vibrometer.Time.y_values.values;
% vib = vi / 5;


% Convert velocity to acceleration
% omega = 2 * pi * freq_vib;
% accel_vib = zeros(size(vib));
% nz = (freq_vib ~= 0);
% accel_vib(nz) = 1i * omega(nz) .* vib(nz);
% accel_vib_mag = abs(accel_vib);

%% --- STEP 3: Plot comparison ---
figure;
plot(freq, accel_x, 'b', 'LineWidth', 1); hold on;
plot(freq, accel_y, 'r', 'LineWidth', 1);
plot(freq, accel_z, 'r', 'LineWidth', 1);
plot(freq, vib, 'r', 'LineWidth', 1);
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title(['Accelerometer vs. Vibrometer' ["Measurement " + file{1}(21)]]);
legend('Vibrometer', 'Accelerometer', 'Location', 'best');
grid on;
set(gca, 'YScale', 'log');
