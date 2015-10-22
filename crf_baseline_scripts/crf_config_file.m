% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.

function [f_load_edges, f_plot, marbl_path]= crf_config_file()

f_load_edges= 1; %0=load previous calculate edge data, 1= calculate group and word edge data
f_plot      = 0; %Plot ROC/PR curves
marbl_path  = ['\home\eswears\Projects\code\marbl']; %Path to marbl toolbox, i.e. parent folder for learn_crf.exe

