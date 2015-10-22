% ckwg +5
% Copyright 2012-2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


function [perf_stats1, cev_cnt]= calculate_perf_stats(labelMatOut, cev_cnt, start_end_terrs, ...
            start_end_PosErrs, cur_evi, cur_ev_type, Param_info, perf_stats1)

for(cli=1:length(labelMatOut))
    labelMat= labelMatOut{cli};
    [scores, IscInd] = sort(labelMat(:,1), 'descend') ;
    labelMat(:,1)= scores;
    labelMat(:,2)= labelMat(IscInd,2);
    th_range1= labelMat(:,1);
    
    perf_stats1(cev_cnt).th_range= [1;th_range1];
    if(~isempty(Param_info) && isfield(Param_info,'FA_area_norm'))
        perf_stats1(cev_cnt).FA_area_norm= Param_info.FA_area_norm;
    end
    
    if(~isempty(Param_info) && isfield(Param_info,'GC_gsd'))
        perf_stats1(cev_cnt).GC_gsd= Param_info.GC_gsd;
    end
    
    %Changed 9/29/14, added ~=0 since missed detects are [0 1] and should not be counted as true positives, given that they will never be detected even at zero threshold
    perf_stats1(cev_cnt).Num_true_pos= [0 cumsum(labelMat(:,2) == 1 & labelMat(:,1) ~= 0)'];
    perf_stats1(cev_cnt).Num_false_pos= [0 cumsum(labelMat(:,2) == 0 & labelMat(:,1) ~= 0)'];
    perf_stats1(cev_cnt).Num_flase_neg= sum(labelMat(:,2) == 1)-perf_stats1(cev_cnt).Num_true_pos;
    perf_stats1(cev_cnt).Num_true_neg = sum(labelMat(:,2) == 0)-perf_stats1(cev_cnt).Num_false_pos;
    
    perf_stats1(cev_cnt).start_end_terrs= start_end_terrs;
    perf_stats1(cev_cnt).start_end_PosErrs= start_end_PosErrs;
    perf_stats1(cev_cnt).labelMat= labelMat;
    perf_stats1(cev_cnt).cur_evi= cur_evi;
    perf_stats1(cev_cnt).cur_ev_type= cur_ev_type;
    cev_cnt= cev_cnt+1;
end
