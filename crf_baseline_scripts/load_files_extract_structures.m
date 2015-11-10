% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function [img_info_list, group_edges, word_edges, same_info_edges, keep_Word_ind_LUT, keep_Group_ind_LUT, cliq_flags]=...
    load_files_extract_structures(img_table_fpath, f_read_all_img_data, img_ind_LUT_fpath,...
    img_ind_table_fpath, num_Feat_Words, num_Feat_Groups, img_edge_table_fpath, f_load_edges, min_Num_Shard_Words, ...
    keep_Word_ind_LUT, keep_Group_ind_LUT, output_path, f_eval)
    

%**************************************************************************************************************
%Image Table **************************************************************************************************************
%Load image table to get train vs test images Ids and the training labels
[img_table_path, img_table_name, img_table_ext]= fileparts(img_table_fpath);
img_table= read_file_into_cellofstrings_v2(img_table_path, [img_table_name img_table_ext]);

img_info_list= extract_image_table_structure(img_table, f_read_all_img_data);

%**************************************************************************************************************
%Image Indicator LookUp Table **************************************************************************************************************
%N-Groups | N-words
%entry_id group-or-word | entry-string
[img_ind_LUT_path, img_ind_LUT_name, img_ind_LUT_ext]= fileparts(img_ind_LUT_fpath);
img_ind_LUT= read_file_into_cellofstrings_v2(img_ind_LUT_path, [img_ind_LUT_name img_ind_LUT_ext]);

%Convert Indicator LookUp Table from file into a data structure
ind_LUT= []; %Index | 0:Group or 1:Word | flickr Group ID mapped to number
for(ri=2:length(img_ind_LUT))
    [LUT_index, LUT_type, LUT_id]= strread(img_ind_LUT{ri}, '%d %s %s');
    ind_LUT= [ind_LUT; LUT_index any([strcmp(LUT_type{1},'W') strcmp(LUT_type{1},'T')])];% str2num(regexprep(LUT_id{1}(2:end-1), '@N',''))];
end

%**************************************************************************************************************
%Image Indicator Table **************************************************************************************************************
%image_id | group_indicator vector | word_indicator vector
[img_ind_table_path, img_ind_table_name,img_ind_table_ext]= fileparts(img_ind_table_fpath);
img_ind_table= read_file_into_cellofstrings_v2(img_ind_table_path, [img_ind_table_name img_ind_table_ext]);

img_info_list= extract_img_ind_table_structure(img_info_list, img_ind_table);

%**************************************************************************************************************
%Calculate frequency of words in title and description and groups
if(isempty(keep_Word_ind_LUT) && isempty(keep_Group_ind_LUT))
    [keep_Word_ind_LUT, keep_Group_ind_LUT]= ...
        determine_most_frequent_values(ind_LUT, img_info_list, num_Feat_Words, num_Feat_Groups);
end
%**************************************************************************************************************
%Edge Table **************************************************************************************************************
%group_edges(img_A_ind,img_B_ind);%number of groups that two images share, group assignments are defined in img_info_list.group_indicator
%word_edges(img_A_ind,img_B_ind,[comments, tags, description, title, any combination])= number of shared words for this category;
%same_info_edges(img_A_ind,img_B_ind,[same user, same location, same contact])= binary
%img_A_ind and img_B_ind are locations/index into img_info_list
if(f_eval==0)
    [group_edges, word_edges, same_info_edges]= create_edge_data_structs(img_edge_table_fpath, 9, 8, f_load_edges, ...
        [img_info_list.ID], keep_Word_ind_LUT, keep_Group_ind_LUT, output_path);
    
    tag_edges= sum(word_edges(:,:,[1:4]),3);%+squeeze(word_edges(:,:,1))+squeeze(word_edges(:,:,3));
    %tag_edges(tag_edges < min_Num_Shard_Words)= 0;
    %group_edges(group_edges < min_Num_Shard_Words)= 0;
    
    cliq_flags= group_edges + tag_edges; % + same_info_edges(:,:,1) + same_info_edges(:,:,2);
else
    group_edges= [];
    word_edges= [];
    same_info_edges= [];
    cliq_flags= [];
end