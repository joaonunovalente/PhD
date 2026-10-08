close all; clear; clc;

% Load all vibrometer measurement files ---
dataFolder = "../data/";
filePattern = fullfile(dataFolder, "measurement_*.1.mat");
files = dir(filePattern);
numFiles = numel(files);

fprintf("Found %d vibrometer measurement files.\n", numFiles);

FRFs_vib = cell(numFiles, 1);
frequencies = cell(numFiles, 1);
angles_deg = zeros(numFiles, 1);

for k = 1:numFiles
    fname = fullfile(files(k).folder, files(k).name);
    data = load(fname);

    % --- Extract vibrometer FRF data ---
    vib = data.vibrometer.FRF.y_values.values / 5;
    freq_inc = data.vibrometer.FRF.x_values.increment;
    num_vals = data.vibrometer.FRF.x_values.number_of_values;
    start_val = data.vibrometer.FRF.x_values.start_value;
    freq = transpose((start_val:num_vals-1) * freq_inc);

    % --- Convert vibrometer velocity to acceleration ---
    omega = 2 * pi * freq;
    accel_vib = zeros(size(vib));
    nz = (freq ~= 0);
    accel_vib(nz) = 1i * omega(nz) .* vib(nz);

    FRFs_vib{k} = accel_vib;
    frequencies{k} = freq;

    % --- Extract angle from filename (e.g., measurement_45.1.mat -> 45°) ---
    tokens = regexp(files(k).name, 'measurement_(\d+)\.1\.mat', 'tokens');
    if ~isempty(tokens)
        angles_deg(k) = str2double(tokens{1}{1});
    else
        angles_deg(k) = (k-1) * (360/numFiles); % fallback
    end
end

% Reference frequency vector & accelerometer data ---
F_ref = frequencies{1};
acc_file = fullfile(dataFolder, "measurement_1.1.mat");
acc_data = load(acc_file);

% Stack vibrometer FRFs into a matrix
numFreq = length(F_ref);
FRF_vib_matrix = zeros(numFreq, numFiles);
for k = 1:numFiles
    FRF_vib_matrix(:, k) = abs(FRFs_vib{k});
end

% Compute mean and standard deviation ---
mean_mag_vib = mean(FRF_vib_matrix, 2);

% Get accelerometer FRF magnitude ---
accel_FRF_mag = abs(acc_data.accelerometer_z.FRF.y_values.values);

% Plot vibrometer FRFs ---
figure;
hold on;
for k = 1:numFiles
    semilogy(F_ref, abs(FRFs_vib{k}), 'Color', [0.7 0.7 0.7]);
end
semilogy(F_ref, accel_FRF_mag, 'r', 'LineWidth', 1.5);
semilogy(F_ref, mean_mag_vib, 'b', 'LineWidth', 1.5);
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('Vibrometer FRFs at Different Angles');
grid on;
set(gca, 'YScale', 'log');

% Plot accelerometer vs. vibrometer mean ---
figure;
semilogy(F_ref, mean_mag_vib, 'b', 'LineWidth', 1.5); hold on;
semilogy(F_ref, accel_FRF_mag, 'r', 'LineWidth', 1.5);
xlabel('Frequency (Hz)');
ylabel('Magnitude (m/s^2/N)');
title('Accelerometer vs. Vibrometer (Mean)');
legend('Vibrometer Mean', 'Accelerometer', 'Location', 'best');
grid on;
set(gca, 'YScale', 'log');
