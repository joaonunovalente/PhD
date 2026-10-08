clear; close all; clc

% Example data: angles in degrees and distances in meters
list = [1 4 5 6 7 8 9];
theta = [0 -13.47 -31.89 -42.5 20.57 36.83 47.86]; % angles in degrees
r = [0.95 0.95 0.95 0.95 0.95 0.95 0.95]; % distances in meters

% Convert angles to radians
theta_rad = deg2rad(theta);

% Create polar plot with markers
polarplot(theta_rad, r, 'ko', 'MarkerSize', 20, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', 'k')
hold on

for i = 1:length(r)
    [theta2,rho] = cart2pol(-i*0.04 + 1.05,-0.9);
    text(theta2,rho, ['Position ' num2str(list(i)) ':  '], ...
        'HorizontalAlignment', 'left', ...
        'VerticalAlignment', 'bottom', ...
        'Color', 'k', 'FontSize', 10, 'FontWeight', 'bold');

    [theta2,rho] = cart2pol(-i*0.04 + 1.05,-0.77);
    text(theta2,rho, [num2str(theta(i), '%.1f') '°'], ...
        'HorizontalAlignment', 'left', ...
        'VerticalAlignment', 'bottom', ...
        'Color', 'k', 'FontSize', 10);

    text(theta_rad(i), r(i), num2str(list(i)), ...
        'HorizontalAlignment', 'center', ...
        'VerticalAlignment', 'middle', ...
        'FontWeight', 'bold', 'Color', 'k', 'FontSize', 10);
end

% Format polar plot
title('Vibrometer Position')
ax = gca;
ax.ThetaLim = [-90 90]; % Show from -90° to 90°
ax.ThetaZeroLocation = 'top'; % 0° line points to the top
ax.ThetaDir = 'clockwise'; % Angles go clockwise

% Increase radial limit to give more space for labels
ax.RLim = [0 1]; % was max(r)+0.05, now more space

% Add grid for better visualization
ax.ThetaGrid = 'on';
ax.RGrid = 'on';
hold off
