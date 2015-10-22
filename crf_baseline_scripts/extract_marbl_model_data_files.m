% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

%******************************************************************************
%Purpose: Define CRF structure and output in marbl model*.txt file format, output node and edge features in data*.txt file format
%   Each data file is mapped to a model file, since they can have a different number of nodes and cliques
%Input:
% keep_Word_ind_LUT: topN most frequent words: %Index | 0:Group or 1:Word | flickr Group ID mapped to number | #times in database
% keep_Group_ind_LUT: topN most frequent groups: %Index | 0:Group or 1:Word | flickr Group ID mapped to number | #times in database
% img_info_list(1)
%           table_ind: 1
%                  ID: 4
%       flickr_img_id: 2.624602947000000e+09
%     flickr_owner_id: 1.113846900000000e+09
%        label_vector: [0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 1 1 -1 1 1 0 1]
%     group_indicator: [4x1 double]
%      word_indicator: [95x1 double]

%output 
%model*.txt: defined here: https://github.com/justindomke/marbl/blob/master/examples/chain_inference.md
%data*.txt: defined here: https://github.com/justindomke/marbl/blob/master/examples/chain_learning.md

function [labels, model]= extract_marbl_model_data_files(cliq_flags, data_locs, TopN, img_info_list, ...
            keep_Word_ind_LUT, keep_Group_ind_LUT, class_ind, group_edges, word_edges, same_info_edges, ...
            model_path, data_path, f_test)

[labels, feats, ~]= extract_feats_labels(data_locs, img_info_list, keep_Word_ind_LUT, keep_Group_ind_LUT, class_ind);

num_nodes= length(data_locs);

%**************************************************************************
%Determine cliques for each image (node) in the database (graph)
ex_data_flags= cliq_flags(data_locs,data_locs);

%Determine cliques for each node
if(0)%BK maximal clique finding algorithm
    cliq_mat= find_maximal_cliques(ex_data_flags, TopN);%some clusters have less than TopN nodes
elseif(0)%Markov Clustering Algorithm (MCL)
    cliq_mat= find_mcl_clusters(ex_data_flags, TopN);
elseif(0)
    cliq_mat= ex_data_flags;

    for(imi=1:num_nodes)
        cur_img_nodes= cliq_mat(imi,:);
        [nodes_val,node_ind]= sort(cur_img_nodes,'descend');
        cliq_mat(imi,node_ind(1:TopN))= 1;
        cliq_mat(imi,node_ind(TopN+1:end))= 0;
    end
else
    cliq_mat= ex_data_flags;
end

nvals= 2; %number of classes not including unlabeled class; class IDs start at 0: 0=unlabeled, 1=other, 2=class of interest
model = database_model(1,length(data_locs),nvals, cliq_mat);%This is the format for the JGMT crf model, but this toolbox only handles pairwise cliques

[efeats] = edgeify_database(group_edges, word_edges, same_info_edges, model.pairs, model.pairtype);

%**********************************************************************************************************************
%Define model*.txt file, where * is the training example index, 
clear model_file
num_edges= length(model.pairs(:,1));

model_file{1}= [num2str(num_nodes)]; %first row is: number of nodes followed by the number of possible values for each node
for(ni=1:num_nodes)
    model_file{1}= [model_file{1} ' 2'];
end
model_file{2}= [num2str(num_nodes + num_edges)] ; %Number of factors (single node and edge) | Bethe Entropy for each factor (single nodes first then pairs)
model_file{3}= [num2str(num_nodes + num_edges)] ; %Number of factors (single node and edge) | list type of factor for each one (0:node vs 1:edge)

for(imi=1:num_nodes)
    %Define Bethe Entropy, 1 for single factors and 1-degrees for cliques
    node_degree= length(find(model.pairs(:)==imi));    
    model_file{2}= [model_file{2} ' ' num2str(1-node_degree)]; %Add single node factor Bethe Entropy of 1
    
    %Define factor type: 0:node, 1:edge
    model_file{3}= [model_file{3} ' 0'];
    
    %Define next single node factor: number of nodes | list of node numbers: numbering starts at zero
    model_file{imi+3}= ['1'];
    model_file{imi+3}= [model_file{imi+3} ' ' num2str(imi-1)];
end

for(pri=1:num_edges)
    %Define Bethe Entropy for pairs, which is "1"
    model_file{2}= [model_file{2} ' 1'];
        
    %Define factor type: 0:node, 1:edge
    model_file{3}= [model_file{3} ' 1'];
    
    %Define next edge node factor: number of nodes | list of node numbers: numbering starts at zero
    model_file{num_nodes+pri+3}= ['2'];
    for(cli=1:2)
        model_file{num_nodes+pri+3}= [model_file{num_nodes+pri+3} ' ' num2str(model.pairs(pri,cli)-1)];
    end
end

write_cellofstrings_into_file(model_path, [], model_file);

%**********************************************************************************************************************
%Define data*.txt file, where * is the same training example index used in the model*.txt file
clear data_file
data_file{1}= [num2str(num_nodes+num_edges)]; %Number of factors

num_feats= length(feats(1,:));

for(imi=1:num_nodes)
    %Define single node features
    data_file{imi+1}= [num2str(num_feats)]; %number of features for this factor | feature values
    for(nfi=1:num_feats)
        data_file{imi+1}= [data_file{imi+1} ' ' num2str(feats(imi,nfi))];
    end
end
   
num_edge_feats= length(efeats(1,:));
for(pri=1:num_edges)
    %Define edge features
    data_file{num_nodes+pri+1}= [num2str(num_edge_feats)]; %number of features for this factor | feature values
    for(nfi=1:num_edge_feats)
        data_file{num_nodes+pri+1}= [data_file{num_nodes+pri+1} ' ' num2str(double(efeats(pri,nfi)>0))];
    end
end
if(f_test==0)
    data_file{end+1}= [num2str(num_nodes)];
    for(imi=1:num_nodes)
        data_file{end}= [data_file{end} ' ' num2str(labels(imi)-1)];
    end
end

write_cellofstrings_into_file(data_path, [], data_file);


%**************************************************************************
%**************************************************************************
function cliq_mat1= find_maximal_cliques(confidence_matrix, TopN)

num_pairs= length(confidence_matrix);

m_ind= sub2ind(size(confidence_matrix),[1:num_pairs],[1:num_pairs]);
cur_discFe3= confidence_matrix>0;
%cur_discFe3(cur_discFe3<0)= cur_discFe3([cur_discFe3<0]');%added for NearHitRun, removed because it resulted in many to one associations
cur_discFe3(cur_discFe3<0)= 0;
cur_discFe3= (cur_discFe3+cur_discFe3')/2;
cur_discFe3(m_ind)= 0;
[MC] = maximalCliques(double(cur_discFe3>0));

%determine number of common nodes
cliq_mat1= zeros(size(confidence_matrix));
for(mci=1:length(MC))
    cur_cliq_nodes= find(MC(:,mci));
    
    cl_weight= [];
    num_clq_nds= length(cur_cliq_nodes);
    for(cli=1:num_clq_nds)
        nd_locs= cur_cliq_nodes(cli);%find(MC(cur_cliq_nodes(cli),mci));
        temp_conf_mat= confidence_matrix(nd_locs,cur_cliq_nodes);
        temp_conf_mat(temp_conf_mat<=0)= [];%zero value usually means that it is the self node, so ignore
        cl_weight(cli)= mean(temp_conf_mat);
    end
    [nodes_val, node_ind]= sort(cl_weight,'descend');
    cliq_mat1(mci, cur_cliq_nodes(node_ind(1:min([num_clq_nds TopN]))))= 1;
end

%**************************************************************************
function cliq_mat1= find_mcl_clusters(confidence_matrix, TopN)
%Markov Clustering Algorithm

clear vertices
[vertices1, vertices2]= find(confidence_matrix);
vertices(:,1) = cellfun(@num2str, num2cell(vertices1), 'uniformoutput', false);
vertices(:,2) = cellfun(@num2str, num2cell(vertices2), 'uniformoutput', false);

weights= confidence_matrix(confidence_matrix>0);
network = getadjacency(vertices, weights);

clusters= mcl(network,'i',3,'m',10); %i=inflation, m=minimum cluster size, clusters have variable number of vertices

cliq_mat1= zeros(size(confidence_matrix));
for(mci=1:length(clusters))
    cur_cliq_nodes= cell2num(cellfun(@str2num, clusters{mci}, 'uniformoutput', false));

    cl_weight= [];
    num_clq_nds= length(cur_cliq_nodes);
    for(cli=1:num_clq_nds)
        nd_locs= cur_cliq_nodes(cli);%find(MC(cur_cliq_nodes(cli),mci));
        temp_conf_mat= confidence_matrix(nd_locs,cur_cliq_nodes);
        temp_conf_mat(temp_conf_mat<=0)= [];%zero value usually means that it is the self node, so ignore
        cl_weight(cli)= mean(temp_conf_mat);
    end
    [nodes_val, node_ind]= sort(cl_weight,'descend');
    cliq_mat1(mci, cur_cliq_nodes(node_ind(1:min([num_clq_nds TopN]))))= 1;   
end




