function [ftrFns, ftrIds, X, varNames] = readFtrsFile( ifn )
% need to keep this in sync with python code for writing features,
% extractFeatures.py

varNames = {};
f = fopen(ifn,'r');
assert( f ~= -1 );
f12 = repmat(' %f', [1,12]);
C = textscan(f,['%q %s %d %f %f %f', f12, f12], ...
    'Delimiter', ',' );
fclose(f);

% Split data out
ftrFns = C{1};
ftrIds = C{2};
n = length(ftrFns);
X = zeros(n,length(C)-2);
for i=1:length(C)-2
    X(:,i) = C{i+2};
end

varNames{end+1} = 'index';
varNames{end+1} = 'confidence';
varNames{end+1} = 'duration';
varNames{end+1} = 'loudness';
for i=1:12
    varNames{end+1} = sprintf('pitch-%02d',i);
end
for i=1:12
    varNames{end+1} = sprintf('timbre-%02d',i);
end

assert(~any(isnan(mat2vec(X(:,3:end)))));