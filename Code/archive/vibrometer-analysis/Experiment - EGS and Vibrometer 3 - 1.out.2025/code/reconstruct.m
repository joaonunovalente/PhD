%% reconstruct_compare_FRF.m
% Compare orthogonal (reference) vs angled vibrometer measurement
% and reconstruct out-of-plane FRF

close all; clear; clc;

%% --- USER PARAMETERS ---
dataFolder = "../data/";
file_ref  = fullfile(dataFolder, "measurement_1.1.mat");  % orthogonal reference
file_angle = fullfile(dataFolder, "measurement_9.1.mat"); % 42.5° angled
theta_deg = 47.9;  % geometric tilt angle (deg)
save_results = true;

fprintf('\n=== Loading FRFs ===\n');

%% --- Load orthogonal (reference) ---
refData = load(file_ref);
H_ref = refData.vibrometer.FRF.y_values.values / 5;   % velocity/force
freq_inc_r = refData.vibrometer.FRF.x_values.increment;
num_vals_r = refData.vibrometer.FRF.x_values.number_of_values;
start_val_r = refData.vibrometer.FRF.x_values.start_value;
freq_ref = transpose((start_val_r:num_vals_r-1) * freq_inc_r);
omega_ref = 2*pi*freq_ref;
H_ref = 1i .* omega_ref .* H_ref;   % convert to acceleration FRF

%% --- Load angled measurement ---
angData = load(file_angle);
H_ang = angData.vibrometer.FRF.y_values.values / 5;
freq_inc_a = angData.vibrometer.FRF.x_values.increment;
num_vals_a = angData.vibrometer.FRF.x_values.number_of_values;
start_val_a = angData.vibrometer.FRF.x_values.start_value;
freq_ang = transpose((start_val_a:num_vals_a-1) * freq_inc_a);
omega_ang = 2*pi*freq_ang;
H_ang = 1i .* omega_ang .* H_ang;

%% --- Align frequency grids ---
f_min = max(min(freq_ref), min(freq_ang));
f_max = min(max(freq_ref), max(freq_ang));
Ncommon = min(length(freq_ref), length(freq_ang));
freq_common = linspace(f_min, f_max, Ncommon).';

H_ref_i = interp1(freq_ref, H_ref, freq_common, 'pchip');
H_ang_i = interp1(freq_ang, H_ang, freq_common, 'pchip');

valid = ~(isnan(H_ref_i) | isnan(H_ang_i));
freq_common = freq_common(valid);
H_ref = H_ref_i(valid);
H_ang = H_ang_i(valid);

%% --- Geometric projection reconstruction ---
fprintf('\n=== Geometric projection (%.2f°) ===\n', theta_deg);
theta = deg2rad(theta_deg);
H_geom = H_ang / cos(theta);

%% --- Complex scalar (α) least-squares reconstruction ---
alpha = sum(H_ref .* conj(H_ang)) / sum(abs(H_ang).^2);
H_alpha = (1/alpha) * H_ang;  % reconstructed out-of-plane
fprintf('alpha magnitude = %.4g, angle = %.3f°\n', abs(alpha), rad2deg(angle(alpha)));

%% --- Helper for metrics ---
compute_metrics = @(Href,Htest) struct( ...
    'MAC', (abs(sum(Href.*conj(Htest)))^2)/(sum(abs(Href).^2)*sum(abs(Htest).^2)), ...
    'corr_abs', abs(sum(Href.*conj(Htest)) / sqrt(sum(abs(Href).^2)*sum(abs(Htest).^2))), ...
    'NRMSE', norm(Href - Htest)/norm(Href), ...
    'mean_mag_ratio_db', mean(20*log10(abs(Href)./abs(Htest)),'omitnan'), ...
    'mean_phase_diff_deg', mean(mod(rad2deg(angle(Href)-angle(Htest))+180,360)-180,'omitnan') ...
);

%% --- Compute metrics ---
M_orig = compute_metrics(H_ref, H_ang);
M_geom = compute_metrics(H_ref, H_geom);
M_alpha = compute_metrics(H_ref, H_alpha);

fprintf('\n=== Comparison metrics ===\n');
fprintf('Original angled FRF:    MAC=%.4f, |corr|=%.4f, NRMSE=%.4f, mean Δφ=%.2f°\n', ...
    M_orig.MAC, M_orig.corr_abs, M_orig.NRMSE, M_orig.mean_phase_diff_deg);
fprintf('Geometric correction:   MAC=%.4f, |corr|=%.4f, NRMSE=%.4f, mean Δφ=%.2f°\n', ...
    M_geom.MAC, M_geom.corr_abs, M_geom.NRMSE, M_geom.mean_phase_diff_deg);
fprintf('α-based reconstruction: MAC=%.4f, |corr|=%.4f, NRMSE=%.4f, mean Δφ=%.2f°\n', ...
    M_alpha.MAC, M_alpha.corr_abs, M_alpha.NRMSE, M_alpha.mean_phase_diff_deg);

%% --- Plots ---
figure('Name','FRF reconstruction comparison','Color','w','Units','normalized','Position',[0.1 0.1 0.7 0.7]);

semilogy(freq_common, abs(H_ref),'k','LineWidth',1.5); hold on;
semilogy(freq_common, abs(H_ang),'b:','LineWidth',1);
semilogy(freq_common, abs(H_geom),'m--','LineWidth',1);
% semilogy(freq_common, abs(H_alpha),'g-.','LineWidth',1);
xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
title('Magnitude comparison');
legend('Ref (orth)','Angled','Geom proj','α-based'); grid on;


figure('Name','FRF reconstruction comparison','Color','w','Units','normalized','Position',[0.1 0.1 0.7 0.7]);
subplot(2,2,1);
semilogy(freq_common, abs(H_ref),'r','LineWidth',1.5); hold on;
semilogy(freq_common, abs(H_ang),'b:','LineWidth',1);
semilogy(freq_common, abs(H_geom),'m--','LineWidth',1);
semilogy(freq_common, abs(H_alpha),'g-.','LineWidth',1);
xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
title('Magnitude comparison');
legend('Ref (orth)','Angled','Geom proj','α-based'); grid on;

subplot(2,2,2);
plot(freq_common, 20*log10(abs(H_ref)./abs(H_ang)),'b:'); hold on;
plot(freq_common, 20*log10(abs(H_ref)./abs(H_geom)),'m--');
plot(freq_common, 20*log10(abs(H_ref)./abs(H_alpha)),'g-.');
xlabel('Frequency (Hz)'); ylabel('Δ|H| (dB)');
title('Magnitude difference (Ref/Test)');
legend('Angled','Geom','α'); grid on;

subplot(2,2,3);
plot(freq_common, mod(rad2deg(angle(H_ref)-angle(H_ang))+180,360)-180,'b:'); hold on;
plot(freq_common, mod(rad2deg(angle(H_ref)-angle(H_geom))+180,360)-180,'m--');
plot(freq_common, mod(rad2deg(angle(H_ref)-angle(H_alpha))+180,360)-180,'g-.');
xlabel('Frequency (Hz)'); ylabel('Phase diff (deg)');
title('Phase difference (wrapped)'); grid on;
legend('Angled','Geom','α');

subplot(2,2,4);
plot(freq_common, abs(H_ref - H_ang),'b:'); hold on;
plot(freq_common, abs(H_ref - H_geom),'m--');
plot(freq_common, abs(H_ref - H_alpha),'g-.');
xlabel('Frequency (Hz)'); ylabel('|ΔH|');
title('Complex error spectrum');
legend('Angled','Geom','α'); grid on;
sgtitle('FRF Reconstruction vs Reference');

%% --- Save results ---
if save_results
    results.freq = freq_common;
    results.H_ref = H_ref;
    results.H_ang = H_ang;
    results.H_geom = H_geom;
    results.H_alpha = H_alpha;
    results.alpha = alpha;
    results.theta_deg = theta_deg;
    results.M_orig = M_orig;
    results.M_geom = M_geom;
    results.M_alpha = M_alpha;
    save(fullfile(dataFolder,'FRF_reconstruction_results.mat'),'results');
    fprintf('\nResults saved to FRF_reconstruction_results.mat\n');
end
