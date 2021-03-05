function [delay, waves, spectra] = extractScan(folder)
% Extract delay scan data_assets into colormap
% folder: Base folder containing delay scan data_assets files
files = dir(folder); files = files(3: end);
specNum = 0;

for fNum = 1: length(files)
    filename = fullfile(folder, files(fNum).name);
    if contains(filename, 'dly')
        delay = double(dlmread(filename));
    elseif contains(filename, 'lambda')
        waves = double(dlmread(filename));
    else
        specNum = specNum + 1 ;
        spectras{specNum} = double(dlmread(filename));
    end
end

spectra = spectras{1};
for i = 2: specNum
   spectra = spectra + spectras{i};
end
spectra = spectra / specNum;

tStart = 45;  % start time of sCFG on probe delay stage
minSpec = 300; maxSpec = 360; % range of spectrometer relevant for sCFG raman_fast

delay = 6.6 * (delay - tStart);
waves = waves(minSpec: maxSpec);
background = mean(spectra(1: tStart - 10, :));
spectra = bsxfun(@minus, spectra, background);  % subtract probe
spectra = spectra .* (spectra > 0);
spectra = spectra(:, minSpec: maxSpec)';
% spectra_display = gBlur(spectra_display, 0.5);
