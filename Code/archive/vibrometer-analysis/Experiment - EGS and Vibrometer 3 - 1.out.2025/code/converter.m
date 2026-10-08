close all; clear; clc; 

accelerometer_x = load("../measurements/measurement_6.1_acc_x.mat")
accelerometer_y = load("../measurements/measurement_6.1_acc_y.mat")
accelerometer_z = load("../measurements/measurement_6.1_acc_z.mat")
vibrometer = load("../measurements/measurement_6.1_vib.mat")

save("measurement_6.1.mat", 'accelerometer_x', 'accelerometer_y', 'accelerometer_z', 'vibrometer');

