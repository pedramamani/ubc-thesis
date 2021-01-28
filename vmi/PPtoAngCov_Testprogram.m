clear all -except keeper
basefolder = 'C:\Users\Ryan\Documents\Data\2020-08-31\test2'; %Nitrogen H Probe data_assets for this
BlackFly = 0; %Otherwise grasshopper on Ryan's
filenames = dir(basefolder);
%Get list of filenames and concatenate into the peakpair array
PeakPairs = [];
for fnum = 3:length(filenames)
    filename(fnum-2) = strcat(basefolder, '\', string(filenames(fnum).name));
    PeakPairs = cat(1,PeakPairs,dlmread(filename(fnum-2)));
end
%
maxions = length(PeakPairs);
ThetaBin = 5;

if BlackFly == 1
    height = 368;
    width = 368;
    centy = 183;
    centx = 188;
    centwid = 1;
    RotAng = -60;
    Rmin = 1;
    Rmax = 100;
    border = 2;
    
else
    height = 600;
    width = 960;
    centy = 505;
    centx = 305;
    centwid = 35;
    RotAng = 0;
    Rmin = 115;
    Rmax = 200;
    border = 25;
end
PeakPairs = PeakPairs(1:maxions,:);

%Mess to image rotate:
[Theta Rho] = cart2pol(PeakPairs(:,2) - centy,PeakPairs(:,1) - centx);
Theta = 180*Theta/pi + RotAng;

% %Preview:
% imshow(PPtoArr_Simple(PeakPairs, height,width))
% axis equal
%
%Select radial range

% This is what I added
PolPairs = [Theta, Rho, PeakPairs(:,3)];
PolPairs = sortrows(PolPairs,2);

first = find(PolPairs(:,2) > Rmin,1,'first');
last = find(PolPairs(:,2) < Rmax,1,'last');

PolPairs = PolPairs(first:last,:);


PolPairs = sortrows(PolPairs,3);
Theta = PolPairs(:,1);
Rho = PolPairs(:,2);
% This is where my stuff ends
    
% for ind = length(PeakPairs):-1:1
%     if (Rho(ind)<Rmin || Rho(ind)>Rmax)
%         Theta(ind) = []; 
%         Rho(ind) = []; 
%         PeakPairs(ind,:) = [];
%     end
% end
[Y, X] = pol2cart(2*pi*Theta/360,Rho);

PeakPairs = [X+centx Y+centy PolPairs(:,3)];

%Cut the border and remove centre: 
for ind = length(PeakPairs):-1:1
    if (PeakPairs(ind,1) < border...
        || PeakPairs(ind,2) < border...
        || PeakPairs(ind,1) > height - border...
        || PeakPairs(ind,2) > width - border)
        PeakPairs(ind,:) = []; 
    end
end

PeakPairs = sortrows(PeakPairs,3);
%Preview:
imshow(PPtoArr_Simple(PeakPairs, height,width))
axis equal
%%
disp('Done clearing middle')

while mod(360,ThetaBin) ~= 0
    ThetaBin = ThetaBin + 1; %Force it to be an integer factor
end

%%
CovTest = PPtoAngCov(PeakPairs,centx,centy,ThetaBin);
%%
%Remove Autovariance
CovImg = BlockCircle(CovTest, 10, round(90/ThetaBin), round(360/ThetaBin - 90/ThetaBin), 0);
CovImg = BlockCircle(CovImg, 10, round(360/ThetaBin-90/ThetaBin), round(360/ThetaBin - 270/ThetaBin), 0);
CovImg = Gblur(CovImg,1);


figure(1)
subplot(2,2,2)
imagesc(PPtoArr_Simple(PeakPairs,height,width))
axis equal
title('Centrifuged - Ion Image')


subplot(2,2,4)
% get the handle to the image
hImg = imagesc(linspace(0,360,ThetaBin),linspace(0,360,ThetaBin),CovImg);
% get the handle to the parent axes
hAxs = get(hImg,'Parent');
% reverse the order of the y-axis tick labels
yAxisTickLabels = get(hAxs, 'YTickLabel');
set(hAxs,'YTickLabel',flipud(yAxisTickLabels));
axis equal
% colormap(inferno)
% caxis([0 max(max(CovImg))])
title('Centrifuged - Angular Covariance')
xlabel('Degrees')
ylabel('Degrees')

