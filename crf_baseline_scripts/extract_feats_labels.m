% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function [labels, feats, img_id]= extract_feats_labels(data_locs, img_info_list, keep_Word_ind_LUT, keep_Group_ind_LUT, class_ind)

num_nodes= length(data_locs);
%extract per image features, just metadata for now:  top 1000 words, and 1000 groups
clear feats labels
labels= [];
img_id= [];
for(imi=1:num_nodes)
    word_ind_vect = img_info_list(data_locs(imi)).word_indicator;
    group_ind_vect= img_info_list(data_locs(imi)).group_indicator;
        
    feats(imi,:)= [ismember(keep_Word_ind_LUT(:,1)',word_ind_vect) ismember(keep_Group_ind_LUT(:,1)',group_ind_vect)];
    
    labels(1,imi)= double(img_info_list(imi).label_vector(class_ind)==1)+1;%0= unlabeled(not used), 1= other class, 2= class of interest 
    
    img_id(1,imi)= img_info_list(data_locs(imi)).ID;
end