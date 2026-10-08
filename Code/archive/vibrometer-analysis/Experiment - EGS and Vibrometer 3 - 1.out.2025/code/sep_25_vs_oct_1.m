close all; clear; clc;

%% --- Load Measurement 1 (0–3500 Hz) ---
m1 = load("../data/measurement_1.1.mat");

accel1 = m1.accelerometer_z.FRF.y_values.values;
vib1 = m1.vibrometer.FRF.y_values.values / 5;

freq_inc1 = m1.vibrometer.FRF.x_values.increment;
num_vals1 = m1.vibrometer.FRF.x_values.number_of_values;
start_val1 = m1.vibrometer.FRF.x_values.start_value;
freq1 = transpose((start_val1:num_vals1-1) * freq_inc1);

%% --- Load Measurement 2 (~0–1200 Hz) ---
m2_acc = load("../data/test/accz");
m2_vib = load("../data/test/vib_1");

accel2 = m2_acc.FRF.y_values.values;
vib2 = m2_vib.FRF.y_values.values;

freq_inc2 = m2_vib.FRF.x_values.increment;
num_vals2 = m2_vib.FRF.x_values.number_of_values;
start_val2 = m2_vib.FRF.x_values.start_value;
freq2 = transpose((start_val2:num_vals2-1) * freq_inc2);

%% --- Convert Vibrometer Velocity to Acceleration ---
omega1 = 2 * pi * freq1;
omega2 = 2 * pi * freq2;

accel_vib1 = zeros(size(vib1));
accel_vib2 = zeros(size(vib2));

nonzero1 = (freq1 ~= 0);
nonzero2 = (freq2 ~= 0);

accel_vib1(nonzero1) = 1i * omega1(nonzero1) .* vib1(nonzero1);
accel_vib2(nonzero2) = 1i * omega2(nonzero2) .* vib2(nonzero2);

%% --- Plot Accelerometer Comparison ---
figure;
semilogy(freq1, abs(accel1), 'b', 'LineWidth', 1.2); hold on;
semilogy(freq2, abs(accel2), 'r--', 'LineWidth', 1.2);
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('Accelerometer Comparison: September 25th vs October 1st');
legend('Measurement 1 (September 25th)', 'Measurement 2 (October 1st)', 'Location', 'best');
grid on;

%% --- Plot Vibrometer Comparison (converted to acceleration) ---
figure;
semilogy(freq1, abs(accel_vib1), 'b', 'LineWidth', 1.2); hold on;
semilogy(freq2, abs(accel_vib2), 'r--', 'LineWidth', 1.2);
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('Vibrometer Comparison: September 25th vs October 1st');
legend('Measurement 1 (September 25th)', 'Measurement 2 (October 1st)', 'Location', 'best');
grid on;


%% --- Optional: Focus on shared frequency range (0–1200 Hz)
idx1 = freq1 <= 1200;
idx2 = freq2 <= 1200;
figure;
semilogy(freq1(idx1), abs(accel1(idx1)), 'b', ...
         freq1(idx1), abs(accel_vib1(idx1)), 'b--', ...
         freq2(idx2), abs(accel2(idx2)), 'r', ...
         freq2(idx2), abs(accel_vib2(idx2)), 'r--');
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('Accelerometer & Vibrometer Comparison (0–1200 Hz)');
legend('M1 Accel', 'M1 Vibro', 'M2 Accel', 'M2 Vibro', 'Location', 'best');
grid on;
