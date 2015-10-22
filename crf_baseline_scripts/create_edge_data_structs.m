% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function [group_edges, word_edges, same_info_edges]= ...
    create_edge_data_structs(img_edge_table_fpath, subi, num_sub, f_load_edges, img_info_list_IDs, ...
    keep_Word_ind_LUT, keep_Group_ind_LUT, output_path)

%image_id | group_indicator vector | word_indicator vector
[img_edge_table_path, img_edge_table_name,img_edge_table_ext]= fileparts(img_edge_table_fpath);

if(f_load_edges==0)
    img_edge_table= read_file_into_cellofstrings_v2(img_edge_table_path, [img_edge_table_name img_edge_table_ext]);
    
    group_edges= zeros(length(img_info_list_IDs));%number of groups that two images share, group assignments are defined in img_info_list.group_indicator
    word_edges=  zeros(length(img_info_list_IDs),length(img_info_list_IDs),5);%number of shared words in (comments, tags, description, title, anycombination)
    same_info_edges=  zeros(length(img_info_list_IDs),length(img_info_list_IDs),3);%same user, same location, same contact 
    num_edges= length(img_edge_table);
    
    row_persub= floor(num_edges/num_sub);%4
    if(subi<num_sub+1)
        row_range= (subi*row_persub-row_persub+1:subi*row_persub);%(631:1260);
        if(subi==num_sub)
            row_range= (subi*row_persub-row_persub+1:num_edges);%(631:1260);
        end
    else
        row_range= 1:num_edges;
    end
    
    max_row= max(row_range);
    for(ri=row_range)
        [ri max_row]
        space_locs= strfind(img_edge_table{ri},' ');
        img_A_id= str2num(img_edge_table{ri}(1:space_locs(1)-1));
        img_A_ind= find(img_info_list_IDs== img_A_id);
        img_B_id= str2num(img_edge_table{ri}(space_locs(1)+1:space_locs(2)-1));
        img_B_ind= find(img_info_list_IDs== img_B_id);
        
%         if(img_A_ind==1 && img_B_ind==57)
%             ri
%         end
%     end
        N_shared_groups= str2num(img_edge_table{ri}(space_locs(2)+1:space_locs(3)-1));
        N_shared_words = str2num(img_edge_table{ri}(space_locs(3)+1:space_locs(4)-1));
        
        if(N_shared_groups>0)
            shared_group_id_vector= img_edge_table{ri}(space_locs(5)+1:space_locs(6)-1);
            
            if(~strcmp(shared_group_id_vector,'none'))
                [shared_group_ids]= strread(shared_group_id_vector, '%d', 'delimiter',',');
                val_group_loc= find(ismember(shared_group_ids,keep_Group_ind_LUT(:,1)));

                group_edges(img_A_ind,img_B_ind)= length(val_group_loc);
            end
        end
        
        %Skip shared_word_id_vector, since this is going to separate that into the different categories (%comments, tags, description, title), can always combine these latter if desired
        
        if(N_shared_words>0)
            shared_word_id_vector= img_edge_table{ri}(space_locs(5)+1:space_locs(6)-1);            
            shared_word_type_vector= img_edge_table{ri}(space_locs(6)+1:space_locs(7)-1);
            
            if(~strcmp(shared_word_type_vector,'none'))
                [shared_word_ids]     = strread(shared_word_id_vector, '%d', 'delimiter',',');
                [shared_word_bitflags]= strread(shared_word_type_vector, '%d', 'delimiter',',');
                
                for(bfi=1:length(shared_word_bitflags))
                    val_word_loc= find(keep_Word_ind_LUT(:,1)==shared_word_ids(bfi));
                    if(~isempty(val_word_loc))
                        cur_bit_flag= dec2bin(shared_word_bitflags(bfi));
                        cur_bit_flag= [repmat('0',1,8-length(cur_bit_flag)) cur_bit_flag];%Make sure it has 8 bits, pad with 0s on left if not
                        cur_bf_int= [];
                        for(bfi2= 1:length(cur_bit_flag))%Convert chars to num
                            cur_bf_int(bfi2)= str2num(cur_bit_flag(bfi2));
                        end
                        img_B_bits= cur_bf_int(1:4);%comments, tags, description, title
                        img_A_bits= cur_bf_int(5:8);
                        shared_locs= find(img_B_bits.*img_A_bits==1);
                        word_edges(img_A_ind, img_B_ind,shared_locs)= word_edges(img_A_ind, img_B_ind,shared_locs)+1;
                        word_edges(img_A_ind, img_B_ind,5)= word_edges(img_A_ind, img_B_ind,5)+ any(img_B_bits)*any(img_A_bits);
                    end
                end
            end
        end
        same_user_flag_str= img_edge_table{ri}(space_locs(7)+1:space_locs(8)-1);
        if(~strcmp(same_user_flag_str,'.') && ~strcmp(same_user_flag_str,'0'))
            same_info_edges(img_A_ind, img_B_ind,1)= str2num(same_user_flag_str);
        end
        
        same_loc_flag_str= img_edge_table{ri}(space_locs(8)+1:space_locs(9)-1);
        if(~strcmp(same_loc_flag_str,'.') && ~strcmp(same_loc_flag_str,'0'))
            same_info_edges(img_A_ind, img_B_ind,2)= str2num(same_loc_flag_str);
        end
        
        same_contact_flag_str= img_edge_table{ri}(space_locs(9)+1:end);
        if(~strcmp(same_contact_flag_str,'.') && ~strcmp(same_contact_flag_str,'0'))
            same_info_edges(img_A_ind, img_B_ind,3)= str2num(same_contact_flag_str);
        end
        if(same_info_edges(img_A_ind, img_B_ind,3)>1)
            dbstop
        end
    end
    if(~exist(output_path))
        mkdir(output_path)
    end
    save([output_path filesep 'edge_data_fr_' num2str(row_range(1)) '-' num2str(row_range(end))],'group_edges','word_edges','same_info_edges')
else
    edge_files= dir([output_path filesep 'edge_data_fr_*']);
    group_edges1= zeros(length(img_info_list_IDs));%number of groups that two images share, group assignments are defined in img_info_list.group_indicator
    word_edges1=  zeros(length(img_info_list_IDs),length(img_info_list_IDs),5);%number of shared words in (title, description, tags, comments, anycombination)
    same_info_edges1= zeros(length(img_info_list_IDs),length(img_info_list_IDs),3);
    
    for(fi=1:length(edge_files))
        load([output_path filesep edge_files(fi).name])
        group_edges1= group_edges1 + group_edges;
        word_edges1 = word_edges1 + word_edges;
        same_info_edges1= same_info_edges1 + same_info_edges;
    end
    group_edges= group_edges1;
    word_edges= word_edges1;
    same_info_edges= same_info_edges1;
end

%Make sure they are symmetric
group_edges= group_edges + group_edges';
for(wi=1:length(word_edges(1,1,:)))
    word_edges(:,:,wi)= word_edges(:,:,wi) +squeeze(word_edges(:,:,wi))';
end
for(wi=1:length(same_info_edges(1,1,:)))
    same_info_edges(:,:,wi)= same_info_edges(:,:,wi) + squeeze(same_info_edges(:,:,wi))';
end
