close all; clear; clc;
% Load data
accelerometer_z = load("../data/test/accz");
vibrometer = load("../data/test/vib_1");

% Frequency vector
increment = vibrometer.FRF.x_values.increment;
number_of_values = vibrometer.FRF.x_values.number_of_values;
start_value = vibrometer.FRF.x_values.start_value;
frequency = transpose((start_value:number_of_values-1) * increment);

% Extract FRF data
accelerometer_z = accelerometer_z.FRF.y_values.values;
vibrometer = vibrometer.FRF.y_values.values;

% Convert vibrometer velocity to acceleration
omega = 2 * pi * frequency;
acceleration_vibrometer = zeros(size(vibrometer));

% Only compute for non-zero frequencies
non_zero_indices = (frequency ~= 0);
acceleration_vibrometer(non_zero_indices) = ...
    1i * omega(non_zero_indices) .* vibrometer(non_zero_indices);

% Plot comparison
semilogy(frequency, abs(accelerometer_z), 'r', ...
         frequency, abs(acceleration_vibrometer), 'b--');
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('September 25^{th} | Accelerometer vs. Vibrometer');
legend('Accelerometer', 'Vibrometer');
grid on;
