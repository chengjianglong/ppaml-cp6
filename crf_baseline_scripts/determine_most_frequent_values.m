% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

%Determine most frequently occurring words and groups, then limit processing to the top num_Feat_Words for each

function [keep_Word_ind_LUT, keep_Group_ind_LUT]= ...
    determine_most_frequent_values(ind_LUT, img_info_list, num_Feat_Words)

word_locs= find(ind_LUT(:,2)==1);
group_locs= find(ind_LUT(:,2)==0);
ind_LUT(:,end+2)= 0;
for(imi=1:length(img_info_list))
    word_indicators= img_info_list(imi).word_indicator;
    word_locs2= word_locs(find(ismember(ind_LUT(word_locs,1),word_indicators)));
    ind_LUT(word_locs2,end-1)= ind_LUT(word_locs2,end-1)+1;
    
    
    group_indicators= img_info_list(imi).group_indicator;
    group_locs2= group_locs(find(ismember(ind_LUT(group_locs,1),group_indicators)));
    ind_LUT(group_locs2,end)= ind_LUT(group_locs2,end)+1;
end

[Y_freq_val,I_freq_ind]= sort(ind_LUT(word_locs,end-1),'descend');
mostFreq_locs= word_locs(I_freq_ind(1:num_Feat_Words));
keep_Word_ind_LUT= ind_LUT(mostFreq_locs,:);

[Y_freq_val,I_freq_ind]= sort(ind_LUT(group_locs,end),'descend');
mostFreq_locs= group_locs(I_freq_ind(1:num_Feat_Words));
keep_Group_ind_LUT= ind_LUT(mostFreq_locs,:);