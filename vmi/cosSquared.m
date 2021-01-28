function [values, mean] = cosSquared(image, rmin)
% Calculate cosine squared about the center of a square image across a range of radii.
% image: to calculate cosine squared of
% rmin: lower bound on radius

[len, ~] = size(image);
radii = rmin: round(len / 2);
[x, y] = meshgrid((1: len) - len / 2, (1: len) - len / 2);
[theta, r] = cart2pol(x, y);
r = round(r);

values = zeros(size(radii));
weights = zeros(size(radii));

for i = 1: length(radii)
    mask = (r == radii(i));
    maskedImage = image(mask);
    maskedTheta = theta(mask);
    weights(i) = sum(maskedImage);
    values(i) = sum(maskedImage ./ weights(i) .* cos(maskedTheta) .^ 2);
end

mean = sum(weights .* values) / sum(weights);
end
