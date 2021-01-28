clear, clc, hold off

DATA_FOLDER = 'data';
BASENAME = '20200902_NO_test*.dat';
HEIGHT = 600; WIDTH = 960;
R_CROP = 200; R_MIN = 50;
CENTER = [300, 520];

image = zeros(HEIGHT, WIDTH);
files = dir(fullfile(DATA_FOLDER, BASENAME))';

for file = files
    [info, ~] = sscanf(file.name, '%d_NO_test%f.dat');
    delay = info(2);
    filename = fullfile(file.folder, file.name);
    
    image = peakHistogram(filename, HEIGHT, WIDTH);
    image = image(CENTER(1) - R_CROP: CENTER(1) + R_CROP - 1, ...
                  CENTER(2) - R_CROP: CENTER(2) + R_CROP - 1);
    [values, mean] = cosSquared(image, R_MIN);
    
    imagesc(image)
    pbaspect([1, 1, 1]);
    title(sprintf('delay = %.0fps, cos2 = %.3f', delay, mean));
    pause(0.5);
end
