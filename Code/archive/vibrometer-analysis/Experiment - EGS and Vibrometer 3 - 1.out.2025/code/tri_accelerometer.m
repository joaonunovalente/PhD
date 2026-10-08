close all; clear; clc;

dataFolder = "../data/";
file_ref  = fullfile(dataFolder, "measurement_1.1.mat");  
file_angle = fullfile(dataFolder, "measurement_9.1.mat"); 
theta_deg = 47.9;

% --- Load reference ---
refData = load(file_ref);
freq = transpose((refData.vibrometer.FRF.x_values.start_value:...
    refData.vibrometer.FRF.x_values.number_of_values-1) * ...
    refData.vibrometer.FRF.x_values.increment);

% Load accelerometer data
H_acc_x = refData.accelerometer_x.FRF.y_values.values;
H_acc_y = refData.accelerometer_y.FRF.y_values.values;
H_acc_z = refData.accelerometer_z.FRF.y_values.values;

% -Load vibrometer data
H_ref = refData.vibrometer.FRF.y_values.values / 5;
omega_ref = 2*pi*freq;
H_ref = 1i*omega_ref.*H_ref;

% --- Load angled ---
angData = load(file_angle);
H_ang = angData.vibrometer.FRF.y_values.values / 5;
omega_ang = 2*pi*freq;
H_ang = 1i*omega_ang.*H_ang;

% --- Geometric reconstruction ---
theta = deg2rad(theta_deg);
H_geom = H_ang / cos(theta);

% --- Plots ---
figure('Color','w');
semilogy(freq(100:end-150), abs(H_ref(100:end-150)),'k','LineWidth',0.5); hold on;
semilogy(freq(100:end-150), abs(H_ang(100:end-150)),'b:','LineWidth',1);
semilogy(freq(100:end-150), abs(H_geom(100:end-150)),'r--','LineWidth',1);
xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
legend('Orthogonal (0º)','Angled (47.9º)','Geometric Projection'); grid on;
title('FRF Magnitudes: Orthogonal vs Measurement 9 (47.9º)');

figure('Color','w');
semilogy(freq(100:end-150), abs(H_acc_x(100:end-150)),'k','LineWidth',0.7); hold on;
semilogy(freq(100:end-150), abs(H_acc_y(100:end-150)),'b:','LineWidth',1);
semilogy(freq(100:end-150), abs(H_acc_z(100:end-150)),'r--','LineWidth',1);
xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
legend('Accelerometer X','Accelerometer Y','Accelerometer Z'); grid on;
title('Accelerometer Tri-Axial');
