% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

% Extract unary and pairwise features for CRF, create marbl model and data
% files for traing and test data, train CRF and then perform inference on
% test data
% - ..._v2.m is adapted to use the PPAML sandbox data and folder structure

function wrapper_crf_database_labeling_v2()

addpath('.')

dbstop if error
f_runscript= 1;

[f_load_edges, f_plot, marbl_path, num_Feat_Words,...
            num_Feat_Groups, nvals, num_class]= crf_config_file();

if(~exist('f_load_edges') || isempty(f_load_edges))
    f_load_edges      = 1; %0=load previous calculate edge data, 1= calculate group and word edge data
else
    if(ischar(f_load_edges))
        f_load_edges= str2num(f_load_edges);
    end
end

if(~exist('f_plot') || isempty(f_plot))
    f_plot              = 0; %Plot ROC/PR curves
else
    if(ischar(f_plot))
        f_plot= str2num(f_plot);
    end
end

%*****************************************************************************************************
if(f_runscript==0)%Use and modify when running directly in matlab, for experimentation purposes
    %Set Parameters
    f_shuffle_data      = 1; %0= load previously shuffled data; 1= randomly shuffle data\
    f_define_train_files= 1; %1= define model*.txt and data*.txt for training data
    f_run_learning      = 1; %0= use previously learned model, 1= learn new model
   
    f_read_all_img_data = 1;%0= only read label_vector of image table (last 24 values, comma separated), 1=read and store all data
    min_Num_Shard_Words = 3;
    TopN                = 10;%Number of nodes (images) to include in clique size
    
    n_fold      = 1; %Number of cross-validation iterations on training data
    num_trian_ex= 2; %Split training data into this many examples
    num_test_ex = 1; %Split testing data into this many examples
else%Use when running from the run.sh or command line
    %Set Parameters
    f_shuffle_data      = 1; %0= load previously shuffled data; 1= randomly shuffle data\
    f_define_train_files= 1; %1= define model*.txt and data*.txt for training data
    f_run_learning      = 1; %0= use previously learned model, 1= learn new model

    f_read_all_img_data = 1;%0= only read label_vector of image table (last 24 values, comma separated), 1=read and store all data
    min_Num_Shard_Words = 3;
    TopN                = 10;%Number of nodes (images) to include in clique size
    
    n_fold      = 1; %Number of cross-validation iterations on training data
    num_trian_ex= 4; %Split training data into this many examples
    num_test_ex = 1; %Split testing data into this many examples
end

%*****************************************************************************************************
%Set Paths for data and outputs ****************************************************************
rel_path= '.';%'C:\';
%marbl_path= [rel_path '\Projects\code\marbl'];

%N-Groups | N-words
%entry_id group-or-word | entry-string | group/word-type-vector
img_ind_LUT_fpath   = [rel_path '\eval_in\etc\image_indicator_lookup_table.txt'];

%image_id | group_indicator | word_indicator
img_ind_table_fpath = [rel_path '\run_in\training\image_indicator_table.txt'];

% image_A_id | image_B_id | N_shared_groups | N_shared_words | shared_group_id_vector | shared_word_id_vector | same_user_flag_id_vector | same_location_flag shared_contact_flag
img_edge_table_fpath= [rel_path '\run_in\training\image_edge_table.txt'];

%image_id | flickr_id | owner_id | title | description | exif_date | exif_time | exif_flash | flickr_location | label_vector (1x24)
img_table_fpath= [rel_path '\run_in\training\image_table.txt'];

%image_id | flickr_id | owner_id | title | description | exif_date | exif_time | exif_flash | flickr_location | label_vector (1x24)
img_table_eval_path= [rel_path '\eval_in\testing\image_table.txt']; %same file as run_in\testing\image_table.txt but with labels filled in

%List of 24 label ids and their string, not needed for processing here, but a good reference if interested in the meaning of the ids
%label_table_path= [rel_path '\eval_in\etc\label_table.txt'];

%Path for model definition (structure), parameters, and data
output_path= [rel_path '\run_out\training'];

if(~exist('marbl_path') || isempty(marbl_path))
    marbl_path= ['\home\eswears\Projects\code\marbl'];
end

if(~ispc)
    img_ind_LUT_fpath   = regexprep(img_ind_LUT_fpath,'\','/');
    img_ind_table_fpath = regexprep(img_ind_table_fpath,'\','/');
    img_edge_table_fpath= regexprep(img_edge_table_fpath,'\','/');
    img_table_fpath     = regexprep(img_table_fpath,'\','/');
    output_path         = regexprep(output_path,'\','/');
    img_table_eval_path = regexprep(img_table_eval_path,'\','/');
    marbl_path = regexprep(marbl_path,'\','/');
end

%Set paths for test data
img_ind_table_fpath_test = regexprep(img_ind_table_fpath,'training','testing');
img_edge_table_fpath_test= regexprep(img_edge_table_fpath,'training','testing');
img_table_fpath_test     = regexprep(img_table_fpath,'training','testing');
output_path_test         = regexprep(output_path,'training','testing');

%*****************************************************************************************************
%Extract features from text files and store in matlab data structures 

%Training featuers
[img_info_list, group_edges, word_edges, same_info_edges, keep_Word_ind_LUT, keep_Group_ind_LUT, cliq_flags]= ...
    load_files_extract_structures(img_table_fpath, f_read_all_img_data, img_ind_LUT_fpath,...
    img_ind_table_fpath, num_Feat_Words, num_Feat_Groups, img_edge_table_fpath, f_load_edges, min_Num_Shard_Words, [], [], output_path, 0);

%Testing features
[img_info_list_test, group_edges_test, word_edges_test, same_info_edges_test, ~, ~, cliq_flags_test]= ...
    load_files_extract_structures(img_table_fpath_test, f_read_all_img_data, img_ind_LUT_fpath,...
    img_ind_table_fpath_test, num_Feat_Words, num_Feat_Groups, img_edge_table_fpath_test, f_load_edges, min_Num_Shard_Words,...
     keep_Word_ind_LUT, keep_Group_ind_LUT, output_path_test, 0);

%Evalutation **************************************************************************************************************
%Get img_info_list_test with evaluation labels for scoring classification results
[img_info_list_eval, ~, ~, ~, ~, ~, ~]= ...
    load_files_extract_structures(img_table_eval_path, f_read_all_img_data, img_ind_LUT_fpath,...
    img_ind_table_fpath_test, num_Feat_Words, num_Feat_Groups, img_edge_table_fpath_test, f_load_edges, min_Num_Shard_Words,...
     keep_Word_ind_LUT, keep_Group_ind_LUT, [], 1);

%**************************************************************************************************************

num_nodes= length(cliq_flags(:,1)); %Number of images in training data
num_test_nodes= length(cliq_flags_test(:,1)); %Number of images in testing data

cv_iter = fix(([1:num_nodes]-1)/(num_nodes-1)*n_fold)+1; %Defines iteration index for positive data to strictly be used for training
cv_iter(cv_iter<1) = 1;
cv_iter(cv_iter>n_fold) = n_fold;

test_data_locs= 1:num_test_nodes; %Use the same test data regardless of cross-validation iteration

clear perf_stats

for(cli=1:num_class)%nvals-1)
    class_ind= cli;
    
    for(cvi=1:n_fold)
        perf_stats.img_ID        = [];
        perf_stats.cvi           = [];
        perf_stats.exi           = [];
        perf_stats.test_data_locs= [];
        perf_stats.truth_labels  = [];
        perf_stats.marginals     = [];
        perf_stats.class_labels  = [];
        perf_stats.Num_TP_correct= [];
        perf_stats.TPC           = [];
        
        %Determine training examples vs test database *******************************
        if(n_fold>1)
            train_data_locs= find(cv_iter~=cvi);        
        else
            train_data_locs= 1:length(cv_iter);        
        end
        num_train_nodes= length(train_data_locs);

        %***********************************************************************************************
        %Training:
        %***********************************************************************************************
        %Define output paths for training
        class_cvi_path_train= [output_path filesep 'class' num2str(cli) filesep 'cvi' num2str(cvi)];
        model_weights_path  = [class_cvi_path_train filesep 'T.txt'];
        
        if(~exist(class_cvi_path_train))
            mkdir(class_cvi_path_train)
        end
        
        %If splitting training data for this cvi into multiple training examples, then randomly shuffle
        if(num_trian_ex>1 && f_shuffle_data==1)
            ex_Traindata_locs= randperm(num_train_nodes);%,ceil(num_nodes/2));
        else
            ex_Traindata_locs= 1:num_train_nodes;
        end
        
        ex_iter = fix((ex_Traindata_locs-1)/(num_train_nodes-1)*num_trian_ex)+1; %Defines iteration index for positive data to strictly be used for training
        ex_iter(ex_iter<1) = 1;
        ex_iter(ex_iter>num_trian_ex) = num_trian_ex;
        if(num_trian_ex>1 && f_shuffle_data==1)
            save([class_cvi_path_train filesep 'train_ex_shuffled.mat'],'ex_iter')
        elseif(num_trian_ex>1)
            try
                load([class_cvi_path_train filesep 'train_ex_shuffled.mat'],'ex_iter')
            catch
               error('Most likely need to set f_shuffule_data to 0') 
            end
        end
                
        if(f_define_train_files==1)
            %Define model and data files for training, one per training example ****************************
            clear train_feats train_labels train_model train_efeats
            for(exi=1:num_trian_ex)
                ex_train_locs= train_data_locs(find(ex_iter==exi));                              
                
                model_path= [class_cvi_path_train filesep 'model' num2str(exi) '.txt'];
                data_path = [class_cvi_path_train filesep 'data' num2str(exi) '.txt'];
                
                extract_marbl_model_data_files(cliq_flags, ex_train_locs, TopN, img_info_list, ...
                    keep_Word_ind_LUT, keep_Group_ind_LUT, class_ind, group_edges, word_edges, ...
                    same_info_edges, model_path, data_path, 0);
            end
        end%else=> Files are already saved, so if not reprocessing then just uses existing files
        
        %Call MARBL learn_CRF executable with model and data files as inputs *************************       
        if(f_run_learning==1)
            system([marbl_path filesep 'learn_CRF -m ' class_cvi_path_train filesep 'model*.txt -d ' class_cvi_path_train filesep 'data*.txt -W ' model_weights_path]);
        end
        %***********************************************************************************************
        %Testing: split test data into multiple groups to speed up clique clustering
        %***********************************************************************************************
        class_cvi_path_test= [output_path_test filesep 'class' num2str(cli) filesep 'cvi' num2str(cvi)];
        if(~exist(class_cvi_path_test))
            mkdir(class_cvi_path_test)
        end
        
        %If splitting testing data into multiple training examples, then randomly shuffle
        if(num_test_ex>1 && f_shuffle_data==1)
            ex_Testdata_locs= randperm(num_test_nodes);%,ceil(num_nodes/2));
        else
            ex_Testdata_locs= 1:num_test_nodes;
        end
        
        exTest_iter = fix((ex_Testdata_locs-1)/(num_test_nodes-1)*num_test_ex)+1; %Defines iteration index for positive data to strictly be used for training
        exTest_iter(exTest_iter<1) = 1;
        exTest_iter(exTest_iter>num_test_ex) = num_test_ex;
        if(num_test_ex>1  && f_shuffle_data==1)
            save([class_cvi_path_test filesep 'test_ex_shuffled.mat'],'exTest_iter')
        elseif(num_test_ex>1)
            load([class_cvi_path_test filesep 'test_ex_shuffled.mat'],'exTest_iter')
        end
        
        for(exi=1:num_test_ex)
            ex_test_locs= test_data_locs(find(exTest_iter==exi));
            
            %Define model and data file for testing, one per testing examples *********************************************
            test_model_path   = [class_cvi_path_test filesep 'test_model' num2str(exi) '.txt'];
            test_data_path    = [class_cvi_path_test filesep 'test_data' num2str(exi) '.txt'];
            marginals_path    = [class_cvi_path_test filesep 'marginals' num2str(exi) '.txt'];
            
            [~, test_model]= extract_marbl_model_data_files(cliq_flags, ex_test_locs, TopN, img_info_list_test, ...
                keep_Word_ind_LUT, keep_Group_ind_LUT, class_ind, group_edges_test, word_edges_test, ...
                same_info_edges_test, test_model_path, test_data_path, 1);
            
            system([marbl_path filesep 'infer_CRF -m ' test_model_path ' -d ' test_data_path ' -w ' model_weights_path ' -mu ' marginals_path ' -i 10']);
            
            %***********************************************************************************************
            %Accumulate values for classification performance metric:
            %***********************************************************************************************
            %Extract truth labels from image_table in eval_in/testing
            [truth_labels, ~, truth_img_IDs]= extract_feats_labels(ex_test_locs, img_info_list_eval, keep_Word_ind_LUT, keep_Group_ind_LUT, class_ind);
            
            %Extract marginal results from marginal.txt and classify (maximum posterior marginal)
            marginal_file= read_file_into_cellofstrings_v2(marginals_path,[]);
            cell_node_marginals= cellfun(@str2num,marginal_file(1:test_model.nnodes),'uniformoutput',false);
            node_marginals= cell2mat(cell_node_marginals(:));
            
            perf_stats.img_ID        = [perf_stats.img_ID truth_img_IDs];
            perf_stats.cvi           = [perf_stats.cvi; ones(length(truth_labels),1)*cvi];
            perf_stats.exi           = [perf_stats.exi; ones(length(truth_labels),1)*exi];
            perf_stats.test_data_locs= [perf_stats.test_data_locs ex_test_locs];
            perf_stats.truth_labels  = [perf_stats.truth_labels truth_labels];
            perf_stats.marginals     = [perf_stats.marginals; node_marginals(:,3)];
            [max_marg,max_labels]= max(node_marginals(:,2:end),[],2);%maximum posterior marginal
            perf_stats.class_labels  = [perf_stats.class_labels; max_labels];
            tr_locs= find(truth_labels==2);
            perf_stats.Num_TP_correct= [perf_stats.Num_TP_correct length(find(abs(truth_labels(tr_locs) - max_labels(tr_locs)')==0))];
            perf_stats.TPC= perf_stats.Num_TP_correct/length(tr_locs); %Number of true postives that were correctly classified
        end        
        save([class_cvi_path_test filesep 'perf_stats_' num2str(cli) '_' num2str(cvi) '.mat'],'perf_stats')%saving each cli and cvi iteration allows us to run multiple matlab sessions in parrallel to speed up processing
    end
end

clear labelMat 
output_labels= zeros(1,nvals);

for(cli2=1:num_class)%:10)%nvals-1)
    labelMat{cli2}= []; %prob | labe (0= other, 1=current class)

    for(cvi=1:n_fold)
        class_cvi_path_test= [output_path_test filesep 'class' num2str(cli2) filesep 'cvi' num2str(cvi)];

        stats_path= [class_cvi_path_test filesep 'perf_stats_' num2str(cli2) '_' num2str(cvi) '.mat'];
        load(stats_path)
        labelMat{cli2}= [labelMat{cli2}; perf_stats.marginals (perf_stats.truth_labels-1)'];
        
        output_labels(perf_stats.test_data_locs,1)= perf_stats.img_ID;   
        output_labels(perf_stats.test_data_locs,cli2+1)= perf_stats.marginals;   
    end
end
[perf_stats_all]= calculate_stats_and_store(labelMat, f_plot);

[perf_stats_all.meanAP]

save([output_path_test filesep 'perf_stats_all.mat'],'perf_stats_all')

%Write out image classification table
[fid,msg1]= fopen([output_path_test filesep 'classified_labels.txt'],'w');
fprintf(fid,['%g ' repmat('%g ',1,nvals-1) '\n'],output_labels');
fclose(fid);

threshold_file= ones(1,nvals-1)*0.5;
%Write out threshold file
[fid,msg1]= fopen([output_path_test filesep 'label_threshold.txt'],'w');
fprintf(fid,[repmat('%f ',1,nvals-1) '\n'],threshold_file');
fclose(fid);

fid;

%**************************************************************************************************************
%*******************************************************************************************
function [perf_stats_out]= calculate_stats_and_store(labelMatOut, f_plot)

perf_stats1= struct([]);
[perf_stats1, cev_cnt]= calculate_perf_stats(labelMatOut, 1, [], ...
    [], 1, 1, [], perf_stats1);

unq_classes= 1:length(labelMatOut);%Based on models not true activities
unq_cl_cell= num2cell(1:length(unq_classes));
%unq_cl_cell{end+1}= [1:length(unq_classes)];

[perf_stats_out]= plot_roc_pr_curves_v2(perf_stats1, unq_cl_cell, unq_classes, f_plot);

%**************************************************************************************************************
%*******************************************************************************************



