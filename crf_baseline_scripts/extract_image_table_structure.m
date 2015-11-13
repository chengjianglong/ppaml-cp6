% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function img_info_list= extract_image_table_structure(img_table, f_read_all_img_data)

img_info_list= struct([]);%.table_ind= [];%%Index into image table file
%img_info_list.ID= [];
%img_info_list.label_vector= [];

for(imi=1:length(img_table))
    space_locs= strfind(img_table{imi},' ');
    quote_locs= strfind(img_table{imi},'"');
    
    cur_img_id         = str2num(img_table{imi}(1:space_locs(1)-1));
    cur_flickr_img_id  = str2num(img_table{imi}(space_locs(1)+1:space_locs(2)-1));
    cur_flickr_owner_id= str2num(regexprep(img_table{imi}(quote_locs(1)+1:quote_locs(2)-1), '@N',''));
    
    if(f_read_all_img_data==1)
        line_ptr= 1;
        title_processed= 0;
        desc_processed = 0;
        exif_processed = 0;
        locality_processed= 0;
        label_processed   = 0;
        for(cli=quote_locs(2)+1:length(img_table{imi}))%scane line looking for each deliminator, space, ", none, comma: trying to get to label_vector, but may need other info, so reading all of it
            if(cli>=line_ptr)
                if(img_table{imi}(cli)=='"' && title_processed==0)%find title surrounded by quotes or none string
                    end_quote_loc= cli+min(strfind(img_table{imi}(cli+1:end),'"'));%should exist
                    cur_title_str= img_table{imi}(cli+1:end_quote_loc-1);%Not currently used for anything
                    line_ptr= end_quote_loc+1;%skip to next character after end quote
                    title_processed= line_ptr;
                elseif(cli+3<=length(img_table{imi}) && strcmp(img_table{imi}(cli:cli+3),'none') && title_processed==0)
                    line_ptr= cli+4; %no title, so skip to next field
                    title_processed= line_ptr;
                elseif(img_table{imi}(cli)=='"' && title_processed>0 && desc_processed==0)%find description surrounded by quotes or none string
                    end_quote_loc= cli+min(strfind(img_table{imi}(cli+1:end),'"'));%should exist
                    cur_desc_str= img_table{imi}(cli+1:end_quote_loc-1);%Not currently used for anything
                    line_ptr= end_quote_loc;%skip to next character after end quote
                    desc_processed= line_ptr;
                elseif(cli+3<=length(img_table{imi}) && strcmp(img_table{imi}(cli:cli+3),'none') && title_processed>0 && desc_processed==0)
                    line_ptr= cli+4; %no title, so skip to next field
                    desc_processed= line_ptr;
                elseif(cli> desc_processed && desc_processed>0 && exif_processed==0)%read exif_date, exif_time, exif_flash
                    space_locs= cli + strfind(img_table{imi}(cli:end),' ')-1;
                    exif_date= img_table{imi}(cli:space_locs(1)-1);
                    exif_time= img_table{imi}(space_locs(1)+1:space_locs(2)-1);
                    exif_flash= img_table{imi}(space_locs(2)+1:space_locs(3)-1);
                    exif_processed= 1;
                    line_ptr= space_locs(3)+1;
                elseif(img_table{imi}(cli)=='"' && exif_processed>0 && locality_processed==0)%find flickr_locality string surrounded by quotes or none string
                    end_quote_loc= cli+min(strfind(img_table{imi}(cli+1:end),'"'));%should exist
                    cur_locality_str= img_table{imi}(cli+1:end_quote_loc-1);%Not currently used for anything
                    line_ptr= end_quote_loc+1;%skip to next character after end quote
                    locality_processed= line_ptr;
                elseif(cli+3<=length(img_table{imi}) && strcmp(img_table{imi}(cli:cli+3),'none') && locality_processed==0)
                    line_ptr= cli+4; %no locality, so skip to next field
                    locality_processed= line_ptr;
                elseif(cli> locality_processed && locality_processed>0 && label_processed==0)
                    label_vector = strread(img_table{imi}(cli:end), '%d', 'delimiter', ',');
                    label_processed= 1;
                    line_ptr= length(img_table{imi})+1;
                end
            end
        end
        comma_locs1= strfind(img_table{imi}(1:end),',');%There are 23 commas between all the label_vectors, labels do not have spaces between them
        last_space1= max(strfind(img_table{imi}(1:comma_locs1(end)),' '));%Last space before end of line
        label_vector1= strread(img_table{imi}(last_space1+1:end), '%d', 'delimiter', ',');
 
        if(label_vector1(1)~=label_vector(1))
            dbstop
        end
    else%only read label_vector
        comma_locs= strfind(img_table{imi}(1:end),',');%There are 23 commas between all the label_vectors, labels do not have spaces between them
        last_space= max(strfind(img_table{imi}(1:comma_locs(end)),' '));%Last space before end of line
        label_vector= strread(img_table{imi}(last_space+1:end), '%d', 'delimiter', ',');
    end
    if(1 || any(label_vector>0) || any(label_vector==-2))
        %img_train_list= [img_train_list; imi cur_img_id label_vector'];%index into img_table | image id | Label ID vector (1x24)
        cur_img_info_list.table_ind   = imi;%index into img_info_list.img_table, img_info_list.image id img_info_list.label_vector (1x24)
        cur_img_info_list.ID          = cur_img_id;
        cur_img_info_list.flickr_img_id   = cur_flickr_img_id;
        cur_img_info_list.flickr_owner_id = cur_flickr_owner_id;
        cur_img_info_list.label_vector= label_vector';
        
        img_info_list= [img_info_list cur_img_info_list];
    end%No test data is in here yet
end