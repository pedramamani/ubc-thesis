function [outarr] = gBlur(inputarray,bluramount)
% Gaussian blurr input array by bluramount
if bluramount ~= 0
    meshsize = ceil(4 * bluramount);
    x = meshgrid(-meshsize: meshsize) .^ 2;
    h = exp(-(x + x') / (2 * bluramount ^ 2));
    outarr = filter2(h, inputarray);
else
    outarr = inputarray;
end
end