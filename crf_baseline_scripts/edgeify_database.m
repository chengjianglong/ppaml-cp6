% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


%group_edges(img_A_ind,img_B_ind);%number of groups that two images share, group assignments are defined in img_info_list.group_indicator
%word_edges(img_A_ind,img_B_ind,[comments, tags, description, title, any combination])= number of shared words for this category;
%same_info_edges(img_A_ind,img_B_ind,[same user, same location, same contact])= binary 
%img_A_ind and img_B_ind are locations/index into img_info_list

function [feats] = edgeify_database(group_edges, word_edges, same_info_edges, pairs, pairtype)

npairs = size(pairs,1);
nfeat= size(group_edges,3)+(size(word_edges,3)-1)+size(same_info_edges,3);
feats = zeros(npairs,nfeat);

pair_ind= sub2ind(size(group_edges),pairs(:,1),pairs(:,2));

feats(:,1)= group_edges(pair_ind);

f_ind=2;
for(fi=1:(size(word_edges,3)-1))%dont use last features=>any combination, since it's highly correlated with the comments feature
    cur_word_mat= squeeze(word_edges(:,:,fi));
    feats(:,f_ind)= cur_word_mat(pair_ind);
    f_ind= f_ind+1;            
end

for(fi=1:size(same_info_edges,3))
    cur_same_mat= squeeze(same_info_edges(:,:,fi));
    feats(:,f_ind)= cur_same_mat(pair_ind);
    f_ind= f_ind+1;            
end

f_ind;