% audioAnalysis.m
%
% Jamie Sherrah  20/July/2013
%
% This is a matlab script to analyse regions of songs based on their
% features.  The aim is to find similarities and clusters.
regionTypes = { 'bars', 'beats', 'sections', 'tatums' };

% Load the data.
for t = 1:length(regionTypes)
    fprintf('Analysing %s...\n', regionTypes{t} );
    % Read this data
    ifn = sprintf('songftrs_%s.csv', regionTypes{t});
    [ftrFns, ftrIds, X, varNames] = readFtrsFile( ifn );
    fnum=1;
    n = size(X,1);
    fprintf('\tThere are %d samples\n',n);
    
    % It's better for clustering and plotting to take the log of the chroma
    % features
    sel = 5:16;
    X(:,sel) = log10(max(1e-3,X(:,sel)));
    
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
    
    if 0
    % Cluster these agglomerative
    D = pdist( X(:,3:end) ); % mode around 15
    figure(fnum); clf; fnum=fnum+1;
    myim(squareform(D));
    title(sprintf('%s: distance matrix',regionTypes{t}));
    Z = linkage(D);
    %figure(fnum); clf; fnum=fnum+1;
    %dendrogram(Z);
    %title(sprintf('%s: dendrogram',regionTypes{t}));
    distThresh = 15.0;
    %T = cluster(Z,'cutoff',distThresh,'criterion','distance');
    T = cluster(Z,'maxclust', 15 );
    else
        nbClusters = floor(sqrt(n/2));
        [T,clc] = kmeans( X(:,3:end), nbClusters );
    end
    fprintf('\tNumber of clusters = %d\n', length(unique(T)));

    figure(fnum); clf; fnum=fnum+1;
    gplotmatrix( X(:,1:16), X(:,17:end), T );
    title(sprintf('%s: ftr grid',regionTypes{t}));

    figure(fnum); clf; fnum=fnum+1;
    scatter3( X(:,4), std(X(:,5:16),0,2), X(:,18), 5, T ); 
    grid on;
    title(sprintf('%s: clusters',regionTypes{t}));
    
    drawnow;
    pause;
end

