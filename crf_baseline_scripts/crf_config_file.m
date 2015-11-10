% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function [f_load_edges, f_plot, marbl_path, num_Feat_Words,...
            num_Feat_Groups, nvals, num_class]= crf_config_file()

f_load_edges= 0; %0=load previous calculate edge data, 1= calculate group and word edge data
f_plot      = 0; %Plot ROC/PR curves
marbl_path  = ['\home\eswears\Projects\code\marbl']; %Path to marbl toolbox, i.e. parent folder for learn_crf.exe
data_type   = 'sandbox'; %'demo','sandbox'

if(strcmp(data_type,'demo'))
    num_Feat_Words      = 10;%Only use the top num_Feat_Words most frequently occurring words
    num_Feat_Groups     = 3;
    nvals  = 3;%Number of labels+1, MIR has 24 labels, add one for "other"
    num_class   = 2;%default= number of classes, but can processes less than the number of classes (nvals-1) to speed things up
elseif(strcmp(data_type,'sandbox'))
    num_Feat_Words      = 1000;%Only use the top num_Feat_Words most frequently occurring words
    num_Feat_Groups     = 1000;
    nvals  = 25;%Number of labels+1, MIR has 24 labels, add one for "other"
    num_class   = 24;%default= number of classes, but can processes less than the number of classes (nvals-1) to speed things up
end
