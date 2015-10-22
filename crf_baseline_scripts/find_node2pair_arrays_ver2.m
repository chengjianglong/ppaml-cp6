% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

%ver2 makes the indexing through model.pairs dependent on the number of paris not the number of cliques
% previous version had the number of cliques equal to the number of pairs, but this is not a general format, can have many pairs in a single clique
function [N1, N2] = find_node2pair_arrays_ver2(model)

% first, just compute # neighbors
NN = zeros(model.nnodes,1);
for(c=1:length(model.pairs(:,1)))
    i = model.pairs(c,1);
    j = model.pairs(c,2);
    NN(i)=NN(i)+1;
    NN(j)=NN(j)+1;
end

%maxN = 4;
maxN = max(NN);
N1 = -1*ones(model.nnodes,maxN);
N2 = -1*ones(model.nnodes,maxN);
index1 = ones(model.nnodes,1);
index2 = ones(model.nnodes,1);
for(c=1:length(model.pairs(:,1)))
    i = model.pairs(c,1);
    j = model.pairs(c,2);
    N1(i,index1(i))=c;
    N2(j,index2(j))=c;
    index1(i)=index1(i)+1;
    index2(j)=index2(j)+1;
end
