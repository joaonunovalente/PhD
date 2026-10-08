close all; clear; clc;
% Load data
measurement_1 = load("../data/measurement_1.1.mat");

% Extract FRF data
accelerometer_z = measurement_1.accelerometer_z.FRF.y_values.values;
vibrometer = measurement_1.vibrometer.FRF.y_values.values / 5;

% Frequency vector
increment = measurement_1.vibrometer.FRF.x_values.increment;
number_of_values = measurement_1.vibrometer.FRF.x_values.number_of_values;
start_value = measurement_1.vibrometer.FRF.x_values.start_value;
frequency = transpose((start_value:number_of_values-1) * increment);

% Convert vibrometer velocity to acceleration
omega = 2 * pi * frequency;
acceleration_vibrometer = zeros(size(vibrometer));

% Only compute for non-zero frequencies
non_zero_indices = (frequency ~= 0);
acceleration_vibrometer(non_zero_indices) = ...
    1i * omega(non_zero_indices) .* vibrometer(non_zero_indices);

% Plot comparison
semilogy(frequency, abs(accelerometer_z), 'b', ...
         frequency, abs(acceleration_vibrometer), 'r--');
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('October 1^{st} | Accelerometer vs. Vibrometer');
legend('Accelerometer', 'Vibrometer');
grid on;
