% audioAnalysis.m
%
% Jamie Sherrah  20/July/2013
%
% This is a matlab script to analyse regions of songs based on their
% features.  The aim is to find similarities and clusters.
regionTypes = { 'bars', 'beats', 'sections', 'tatums' };

% Load the data.
for t = 1 % 1:length(regionTypes)
    fprintf('Analysing %s...\n', regionTypes{t} );
    % Read this data
    ifn = sprintf('songftrs_%s.csv', regionTypes{t});
    [ftrFns, X, varNames] = readFtrsFile( ifn );
    fnum=1;
    
    idxConf = strmatch('confidence',varNames);
    idxDurn = strmatch('duration',varNames);
    idxLoud = strmatch('loudness',varNames);
    idxPitch= idxLoud + [1:12];
    idxTimb = idxPitch+12;
    
    nbins = 200;
    % confidence hist
    figure(fnum); clf; fnum=fnum+1;
    hist( X(:,idxConf), nbins );
    grid on;
    title(sprintf('%s: Confidence histogram',regionTypes{t}));
    
    % duration hist
    figure(fnum); clf; fnum=fnum+1;
    hist( X(:,idxDurn), nbins );
    grid on;
    title(sprintf('%s: Duration histogram',regionTypes{t}));
    
    % loudness hist
    figure(fnum); clf; fnum=fnum+1;
    hist( X(:,idxLoud), nbins );
    grid on;
    title(sprintf('%s: Loudness histogram',regionTypes{t}));
    
    % pitch
    figure(fnum); clf; fnum=fnum+1;
    gplotmatrix( X(:,idxPitch) );
    title(sprintf('%s: pitch',regionTypes{t}));
    
    % timbre
    figure(fnum); clf; fnum=fnum+1;
    gplotmatrix( X(:,idxTimb) );
    title(sprintf('%s: timbre',regionTypes{t}));
    
    drawnow;
    %pause;
end

