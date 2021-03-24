clear, clc;
[delay, waves, specNotch] = extractScan('.\data\notch4');
[~, ~, specFull] = extractScan('.\data\nom1');

desc = 'Raman of 9ps piercing at 1.5THz (0.5atm O2 @ 3.8mJ sCFG)';
% desc = 'Raman unpierced (0.5atm O2 @ 3.8mJ sCFG)';
cbounds = [1E3, 1E5]; % thresholded log values on plot

figure(1);
% imagesc(delay, waves, specFull)
surf(delay, waves, specFull)
xlabel('Probe Delay (ps)')
ylabel('Raman Signal (nm)')
title(desc)
colorbar
set(gca,'ColorScale', 'log')
caxis(cbounds)
xlim([0, inf])
