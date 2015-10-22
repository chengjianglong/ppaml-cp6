% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function img_info_list= extract_img_ind_table_structure(img_info_list, img_ind_table)

for(ri=1:length(img_ind_table))
    space_locs= strfind(img_ind_table{ri},' ');
    cur_img_id= str2num(img_ind_table{ri}(1:space_locs(1)-1));
    img_loc= find([img_info_list.ID]==cur_img_id);
    
    group_string= img_ind_table{ri}(space_locs(1)+1:space_locs(2)-1);
    if(~strcmp(group_string,'none'))
        [group_indicators]= strread(group_string, '%d', 'delimiter',',');
        img_info_list(img_loc).group_indicator= group_indicators;%Pointers to ids in LUT
    else
        img_info_list(img_loc).group_indicator= [];
    end
    
    word_string= img_ind_table{ri}(space_locs(2)+1:space_locs(3)-1);
    if(~strcmp(word_string,'none'))
        [word_indicators]= strread(word_string, '%d', 'delimiter',',');
        img_info_list(img_loc).word_indicator= word_indicators;%Pointers to ids in LUT
    else
        img_info_list(img_loc).word_indicator= [];
    end
end