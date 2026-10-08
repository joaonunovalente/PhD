%% compare_FRFs_metrics.m
close all; clear; clc;

%% --- PARAMETERS ---
dataFolder = "../data/";
file = fullfile(dataFolder, "measurement_8.1.mat");

%% --- STEP 1: Load data ---

% Accelerometer FRF (complex, acceleration/force)
accData = load(file);
H_acc = accData.accelerometer_z.FRF.y_values.values;   % complex FRF
freq_inc_a = accData.accelerometer_z.FRF.x_values.increment;
num_vals_a = accData.accelerometer_z.FRF.x_values.number_of_values;
start_val_a = accData.accelerometer_z.FRF.x_values.start_value;
freq_acc = transpose((start_val_a:num_vals_a-1) * freq_inc_a);

% Vibrometer FRF (complex, velocity/force)
vibData = load(file);
H_vel = vibData.vibrometer.FRF.y_values.values / 5;    % scaled velocity FRF
freq_inc_v = vibData.vibrometer.FRF.x_values.increment;
num_vals_v = vibData.vibrometer.FRF.x_values.number_of_values;
start_val_v = vibData.vibrometer.FRF.x_values.start_value;
freq_vib = transpose((start_val_v:num_vals_v-1) * freq_inc_v);

% Convert velocity FRF to acceleration FRF
omega = 2 * pi * freq_vib;
H_vib = 1i .* omega .* H_vel;   % acceleration/force (complex)

%% --- STEP 2: Align frequency grids ---
f_min = max(min(freq_acc), min(freq_vib));
f_max = min(max(freq_acc), max(freq_vib));
Ncommon = min(length(freq_acc), length(freq_vib));
freq_common = linspace(f_min, f_max, Ncommon).';

H_acc_i = interp1(freq_acc, H_acc, freq_common, 'pchip');
H_vib_i = interp1(freq_vib, H_vib, freq_common, 'pchip');

% Remove invalid (NaN) points
valid = ~(isnan(H_acc_i) | isnan(H_vib_i));
freq_common = freq_common(valid);
H_acc = H_acc_i(valid);
H_vib = H_vib_i(valid);

%% --- STEP 3: Clean and prepare data ---
Mag_acc = abs(H_acc);
Mag_vib = abs(H_vib);

% Remove DC (0 Hz) and near-zero or invalid magnitudes
eps_th = 1e-12;
invalid = (freq_common == 0) | isnan(Mag_acc) | isnan(Mag_vib) | (Mag_vib < eps_th);
freq_common(invalid) = [];
H_acc(invalid) = [];
H_vib(invalid) = [];
Mag_acc(invalid) = [];
Mag_vib(invalid) = [];

if isempty(H_acc)
    error('No valid data after cleaning. Check FRF contents or interpolation range.');
end

Phase_acc = unwrap(angle(H_acc));
Phase_vib = unwrap(angle(H_vib));
Phase_diff = Phase_acc - Phase_vib;
Phase_diff_deg = rad2deg(Phase_diff);

%% --- STEP 4: Compute metrics ---
% --- Magnitude ratio ---
mag_ratio = Mag_acc ./ Mag_vib;
mag_ratio_db = 20 * log10(mag_ratio);
mean_mag_ratio = mean(mag_ratio, 'omitnan');
mean_mag_ratio_db = mean(mag_ratio_db, 'omitnan');
std_mag_ratio = std(mag_ratio, 'omitnan');

% --- Normalized RMSE ---
NRMSE_complex = norm(H_acc - H_vib) / norm(H_vib);
NRMSE_mag = norm(Mag_acc - Mag_vib) / norm(Mag_vib);

% --- MAC (Modal Assurance Criterion) ---
num = abs(sum(H_acc .* conj(H_vib)))^2;
den = sum(abs(H_acc).^2) * sum(abs(H_vib).^2);
MAC = num / den;

% --- Complex correlation coefficient ---
corr_val = sum(H_acc .* conj(H_vib)) / sqrt(sum(abs(H_acc).^2) * sum(abs(H_vib).^2));
corr_abs = abs(corr_val);

% --- Phase metrics ---
mean_abs_phase_err = mean(abs(Phase_diff_deg), 'omitnan');
rms_phase_err = sqrt(mean(Phase_diff_deg.^2, 'omitnan'));

%% --- STEP 5: Print results ---
fprintf('\n--- FRF Comparison Metrics ---\n');
fprintf('Frequency range: %.1f – %.1f Hz (%d pts)\n\n', freq_common(1), freq_common(end), length(freq_common));

fprintf('Mean magnitude ratio: %.4f ± %.4f\n', mean_mag_ratio, std_mag_ratio);
fprintf('Mean magnitude ratio (dB): %.3f dB\n', mean_mag_ratio_db);
fprintf('NRMSE (complex): %.4f\n', NRMSE_complex);
fprintf('NRMSE (magnitude): %.4f\n', NRMSE_mag);
fprintf('Complex correlation coefficient: %.4f (|r|)\n', corr_abs);
fprintf('MAC: %.4f\n', MAC);
fprintf('Mean abs. phase error: %.3f°\n', mean_abs_phase_err);
fprintf('RMS phase error: %.3f°\n\n', rms_phase_err);

%% --- STEP 6: Plots ---
figure('Name','FRF Comparison','Color','w');

subplot(2,2,1);
semilogy(freq_common, Mag_vib, 'b', 'LineWidth', 1); hold on;
semilogy(freq_common, Mag_acc, 'r', 'LineWidth', 1);
xlabel('Frequency (Hz)'); ylabel('|H| (m/s^2/N)');
title('FRF Magnitude');
legend('Vibrometer→Accel','Accelerometer','Location','best'); grid on;

subplot(2,2,2);
plot(freq_common, mag_ratio_db, 'k', 'LineWidth', 1);
xlabel('Frequency (Hz)'); ylabel('ΔMag (dB)');
title('Magnitude Ratio (Acc/Vib)');
grid on;

subplot(2,2,3);
plot(freq_common, Phase_diff_deg, 'm', 'LineWidth', 1);
xlabel('Frequency (Hz)'); ylabel('Phase diff (°)');
title('Phase Difference (Acc - Vib)');
grid on;

subplot(2,2,4);
plot(freq_common, abs(H_acc - H_vib), 'g', 'LineWidth', 1);
xlabel('Frequency (Hz)'); ylabel('|ΔH| (m/s^2/N)');
title('Complex Error Spectrum');
grid on;

sgtitle('Accelerometer vs Vibrometer FRF Comparison');

%% --- STEP 7: Save metrics ---
metrics.freq = freq_common;
metrics.H_acc = H_acc;
metrics.H_vib = H_vib;
metrics.MAC = MAC;
metrics.corr_abs = corr_abs;
metrics.NRMSE_complex = NRMSE_complex;
metrics.NRMSE_mag = NRMSE_mag;
metrics.mean_mag_ratio = mean_mag_ratio;
metrics.mean_mag_ratio_db = mean_mag_ratio_db;
metrics.std_mag_ratio = std_mag_ratio;
metrics.mean_abs_phase_err = mean_abs_phase_err;
metrics.rms_phase_err = rms_phase_err;

save(fullfile(dataFolder, 'FRF_metrics.mat'), 'metrics');
fprintf('Metrics saved to FRF_metrics.mat\n');


%% --- RECONSTRUCT & COMPARE: complex-scalar alignment & geometric projection ---
% Assumes: freq_common, H_acc (reference out-of-plane), H_vib (measured angled) exist.

% User: set geometric angle of the vibrometer relative to out-of-plane (deg)
% If unknown, set [] to skip geometric projection
theta_deg = 42.5;    % <-- set to measured tilt (deg) OR [] to skip

% Helper: metrics function (returns struct)
function M = compute_metrics(Href, Htest)
    % remove tiny/NaN points
    eps_th = 1e-12;
    valid = ~(isnan(Href) | isnan(Htest) | (abs(Htest) < eps_th));
    Href = Href(valid);
    Htest = Htest(valid);

    M.Mag_ref = abs(Href);
    M.Mag_test = abs(Htest);
    M.Ph_ref = angle(Href);
    M.Ph_test = angle(Htest);
    M.Ph_diff_raw_deg = rad2deg(M.Ph_ref - M.Ph_test);
    % wrap to [-180,180]
    M.Ph_diff_wrapped_deg = mod(M.Ph_diff_raw_deg + 180, 360) - 180;

    % magnitude ratio (linear & dB)
    M.mag_ratio = M.Mag_ref ./ M.Mag_test;
    M.mag_ratio_db = 20*log10(M.mag_ratio);

    % summary stats
    M.mean_mag_ratio = mean(M.mag_ratio, 'omitnan');
    M.std_mag_ratio  = std(M.mag_ratio, 'omitnan');
    M.mean_mag_ratio_db = mean(M.mag_ratio_db, 'omitnan');

    % NRMSE
    M.NRMSE_complex = norm(Href - Htest) / norm(Href);
    M.NRMSE_mag = norm(M.Mag_ref - M.Mag_test)/norm(M.Mag_ref);

    % correlation and MAC
    cnum = sum(Href .* conj(Htest));
    M.complex_corr = cnum / sqrt(sum(abs(Href).^2) * sum(abs(Htest).^2));
    M.complex_corr_abs = abs(M.complex_corr);
    M.MAC = (abs(cnum)^2) / (sum(abs(Href).^2) * sum(abs(Htest).^2));

    % phase circular stats
    a = exp(1j*deg2rad(M.Ph_diff_wrapped_deg));
    R = sum(a)/length(a);
    M.circular_mean_deg = rad2deg(angle(R)); % mean phase offset
    % circular std (approx): sqrt(-2 ln |R|) in radians
    M.circular_std_deg = sqrt(-2*log(abs(R))) * (180/pi);

    M.mean_abs_phase_wrapped = mean(abs(M.Ph_diff_wrapped_deg));
    M.rms_phase_wrapped = sqrt(mean(M.Ph_diff_wrapped_deg.^2));
end

% --- Original metrics (before correction)
M_orig = compute_metrics(H_acc, H_vib);

% --- 1) Optimal complex scalar alpha: H_acc ≈ alpha * H_vib  =>  alpha = <H_acc,H_vib> / <H_vib,H_vib>
alpha = sum(H_acc .* conj(H_vib)) / sum(abs(H_vib).^2);
alpha_mag = abs(alpha);
alpha_phase_deg = rad2deg(angle(alpha));
H_vib_alpha = alpha * H_vib;        % aligned to H_acc
% Reconstruct H_out from measured H_vib by inverse scaling:
H_recon_from_alpha = (1/alpha) * H_vib;   % best LS estimate of H_acc from H_vib

M_alpha_before = compute_metrics(H_acc, H_vib_alpha);   % how close alpha*H_vib is to H_acc
M_alpha_after  = compute_metrics(H_acc, H_recon_from_alpha); % how close reconstructed is

% --- 2) Geometric projection correction (if theta provided)
if ~isempty(theta_deg)
    % Model: H_meas = cos(theta)*H_out + sin(theta)*H_in
    % If H_in negligible, H_out = H_meas / cos(theta)
    theta = deg2rad(theta_deg);
    cosf = cos(theta);
    if abs(cosf) < 1e-6
        warning('cos(theta) ~ 0; geometric projection unstable.');
        H_proj_recon = H_vib; % fallback
    else
        H_proj_recon = H_vib / cosf;    % amplitude correction (phase unchanged)
    end
    M_proj = compute_metrics(H_acc, H_proj_recon);
else
    M_proj = [];
    H_proj_recon = [];
end

% --- Print a concise comparison table ---
fprintf('\n--- Reconstruction summary ---\n');
fprintf('Alpha (complex LS): |alpha| = %.5g, angle = %.3f deg\n', alpha_mag, alpha_phase_deg);
fprintf('Original:    MAC=%.4f | corr=%.4f | NRMSE_c=%.4f | mean abs phase(wrapped)=%.3f deg\n', ...
    M_orig.MAC, M_orig.complex_corr_abs, M_orig.NRMSE_complex, M_orig.mean_abs_phase_wrapped);

fprintf('After alpha*H_vib: MAC=%.4f | corr=%.4f | NRMSE_c=%.4f | mean abs phase(wrapped)=%.3f deg\n', ...
    M_alpha_before.MAC, M_alpha_before.complex_corr_abs, M_alpha_before.NRMSE_complex, M_alpha_before.mean_abs_phase_wrapped);

fprintf('Reconstructed H_out (1/alpha * H_vib): MAC=%.4f | corr=%.4f | NRMSE_c=%.4f | mean abs phase(wrapped)=%.3f deg\n', ...
    M_alpha_after.MAC, M_alpha_after.complex_corr_abs, M_alpha_after.NRMSE_complex, M_alpha_after.mean_abs_phase_wrapped);

if ~isempty(M_proj)
    fprintf('Geometric proj (theta=%.2f°): MAC=%.4f | corr=%.4f | NRMSE_c=%.4f | mean abs phase(wrapped)=%.3f deg\n', ...
        theta_deg, M_proj.MAC, M_proj.complex_corr_abs, M_proj.NRMSE_complex, M_proj.mean_abs_phase_wrapped);
end

% show a few more useful scalars
fprintf('\nMean magnitude ratio (orig) = %.3g ± %.3g (linear), %.3f dB (mean)\n', ...
    M_orig.mean_mag_ratio, M_orig.std_mag_ratio, M_orig.mean_mag_ratio_db);

% --- Plots: compare amplitude & phase
figure('Name','Reconstruction diagnostics','Color','w','Units','normalized','Position',[.1 .1 .7 .6]);
subplot(2,2,1);
semilogy(freq_common, abs(H_acc),'r'); hold on;
semilogy(freq_common, abs(H_vib),'b:');
semilogy(freq_common, abs(H_recon_from_alpha),'g--'); % 1/alpha * H_vib
if ~isempty(H_proj_recon), semilogy(freq_common, abs(H_proj_recon),'m-.'); end
xlabel('Freq (Hz)'); ylabel('|H|'); legend('Ref (orth)','H\_meas','Recon (1/alpha)','GeomProj'); title('Amplitude');

subplot(2,2,2);
plot(freq_common, 20*log10(abs(H_acc)) - 20*log10(abs(H_vib)),'k'); hold on;
plot(freq_common, 20*log10(abs(H_acc)) - 20*log10(abs(H_recon_from_alpha)),'g');
if ~isempty(H_proj_recon), plot(freq_common, 20*log10(abs(H_acc)) - 20*log10(abs(H_proj_recon)),'m'); end
xlabel('Freq (Hz)'); ylabel('ΔMag (dB)'); title('Mag diff (Ref - test)'); legend('orig','1/alpha','geom');

subplot(2,2,3);
ph_ref = rad2deg(angle(H_acc));
ph_meas = rad2deg(angle(H_vib));
ph_recA = rad2deg(angle(H_recon_from_alpha));
plot(freq_common, ph_ref,'r'); hold on; plot(freq_common, ph_meas,'b:'); plot(freq_common, ph_recA,'g--');
xlabel('Freq (Hz)'); ylabel('Phase (deg)'); title('Phase'); legend('Ref','Meas','Recon 1/alpha');

subplot(2,2,4);
plot(freq_common, mod(rad2deg(angle(H_acc) - angle(H_recon_from_alpha))+180,360)-180,'g'); hold on;
plot(freq_common, mod(rad2deg(angle(H_acc) - angle(H_vib))+180,360)-180,'b:');
if ~isempty(H_proj_recon), plot(freq_common, mod(rad2deg(angle(H_acc) - angle(H_proj_recon))+180,360)-180,'m-.'); end
xlabel('Freq (Hz)'); ylabel('Phase diff (deg)'); title('Phase diff (wrapped)'); legend('1/alpha','orig','geom');

sgtitle('Comparison: Reference (orth) vs Measured & Reconstructed');

% optional save
save(fullfile(dataFolder,'reconstruction_comparison.mat'),'M_orig','M_alpha_before','M_alpha_after','M_proj','alpha');

