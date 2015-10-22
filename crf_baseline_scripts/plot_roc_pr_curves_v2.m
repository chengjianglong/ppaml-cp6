% ckwg +5
% Copyright 2013-2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


function [perf_stats]=plot_roc_pr_curves_v2(perf_stats, unq_cl_cell, unq_classes, f_plot)
dbstop if error

if(f_plot)
    fig1= gcf; hold on
    %fig1= figure; hold on
    cl_colors= rand(length(unq_cl_cell),3);
    if(length(unq_cl_cell)==7) %WAND
        cl_colors= [0 1 0;    .125 1 .875;   1 .563 0; 0 0 1;  .75 0 .75;  1 1 0; 0 0 0];
    elseif(length(unq_cl_cell)==6) %OC :  parking-spots, road,  sidewalk, doorway, building, all
        cl_colors= [ 1 .563 0;   0 0 1; .75 0 .75;   1 0 0; 0 1 0;  0 0 0];
        %           orange     blue    purple    yellow   green black
        
        %cl_colors= [1 0 0; 0 1 0; 0 0 1; .75 0 .75; 0 0 0; 1 .563 0];%cell PIM data
    elseif(length(unq_cl_cell)==5) %WASL :  building, road-main, road-size, intersection, all
        cl_colors= [ 1 .563 0;   0 0 1; .75 0 .75;   1 0 0; 0 0 0];%fourth one was yellow, changed to red since it's easier to see
        %           orange     blue    purple    red   green
    elseif(length(unq_cl_cell)==4) %WASL :  building, road-main, road-size, intersection, all
        cl_colors= [ 1 .563 0;   0 0 1; 1 0 0;  0 1 0];
        %           orange     blue    yellow   green
    elseif(length(unq_cl_cell)==21)
        cl_colors= colormap(lines(22));
        warning('need to define colors for this dataset')
    end
    
    %fig2= figure; hold on
end

for(cli=1:length(unq_cl_cell))
    %class_pcc(cli)= class_norm_pred
    cur_cl_loc= unq_cl_cell{cli};
    out_loc= cur_cl_loc;
    
    if(length(cur_cl_loc)>1)
        out_loc= max(cur_cl_loc)+1;
    end
    
    if(isfield(perf_stats(cur_cl_loc),'GC_gsd'))
        GC_gsd= perf_stats(cur_cl_loc(1)).GC_gsd;
        gsd_str= 'Area';
    else
        GC_gsd= 1;
        gsd_str= '';
    end
    
    %PR Curve
    if(~isempty(perf_stats(cur_cl_loc).Num_true_pos))
        num_true_pos = [perf_stats(cur_cl_loc).Num_true_pos].*GC_gsd;
        num_false_neg= [perf_stats(cur_cl_loc).Num_flase_neg].*GC_gsd;
        num_false_pos= [perf_stats(cur_cl_loc).Num_false_pos].*GC_gsd;
        num_true_neg = [perf_stats(cur_cl_loc).Num_true_neg].*GC_gsd;
        thresh1      = vertcat(perf_stats(cur_cl_loc).th_range)';
        
        tpfn_denom= (num_true_pos+num_false_neg+eps);
        Recall= (num_true_pos)./tpfn_denom;%sensitivity
        tpfp_denom= (num_true_pos+num_false_pos+eps);
        Precision= (num_true_pos)./tpfp_denom;
        
        %ROC Curve
        TruePosRate= (num_true_pos)./tpfn_denom;
        fptn_denom= (num_false_pos+num_true_neg+eps);
        if(isfield(perf_stats(cur_cl_loc),'FA_area_norm'))
            FalsePosRate= (num_false_pos)*perf_stats(cur_cl_loc(1)).FA_area_norm;
        else
            FalsePosRate= (num_false_pos)./fptn_denom;
        end
        
        %     TN_rate= sum(perf_stats.Num_true_neg(:,cur_cl_loc),2)./...
        %         (sum(perf_stats.Num_false_pos(:,cur_cl_loc),2)+sum(perf_stats.Num_true_neg(:,cur_cl_loc),2));
        neg_denom= (num_false_neg+num_true_neg+eps);
        TrueNegRate= (num_true_neg)./neg_denom;%specificity
        FlaseNegRate= (num_false_neg)./neg_denom;
        
        accuracy_num=  (num_true_pos + num_true_neg+eps);
        accuracy_den= accuracy_num + (num_false_pos + num_false_neg);
        perf_stats(out_loc).accuracy_meas= accuracy_num./accuracy_den;
        perf_stats(out_loc).segemtnation_accuracy_meas= num_true_pos./(num_true_pos + num_false_pos + num_false_neg);
        
        %Find Cutoff point on ROC curve **********************************************************
        yroc= TruePosRate;%flipud([1; 1-FalsePosRate; 0]);
        xroc= FalsePosRate;%flipud([1; 1-TruePosRate; 0]); %ROC points
        
        %thresh1= perf_stats(cur_cl_loc).th_range';
        if(length(FalsePosRate)>1)
            roc_area=trapz([FalsePosRate'],[TruePosRate']); %estimate the area under the curve
        else
            roc_area= 0;
        end
        
        %Find point closest to (0,1)
        d= realsqrt(xroc.^2+(1-yroc).^2); %apply the Pythagorean theorem
        
        %Calculate Confusion Matrix based on ROC performance
        [co_threshROC,thresh_indexROC]= min(d); %find the least distance
        perf_stats(out_loc).cut_off_pointROC= thresh1(thresh_indexROC); %Set the cut-off point
        perf_stats(out_loc).cut_off_valueROC= co_threshROC;
        perf_stats(out_loc).conf_matROC     = [num_true_pos(thresh_indexROC) num_false_neg(thresh_indexROC);...
            num_false_pos(thresh_indexROC) num_true_neg(thresh_indexROC)];
        perf_stats(out_loc).Norm_conf_matROC= perf_stats(out_loc).conf_matROC./repmat(sum(perf_stats(out_loc).conf_matROC,2),1,2);
        %**************************************************************************
        
        %roc_area= calculate_roc_area(FalsePosRate,TruePosRate);
        [minv,thresh_loc]= min(abs(thresh1-.5));
        
        f_meas= 2*(Recall.*Precision)./(Recall+Precision);
        [maxFmeas,thresh_loc]= max(f_meas);
        
        perf_stats(out_loc).CLI_Recall= Recall;
        perf_stats(out_loc).CLI_Precision= Precision;
        perf_stats(out_loc).CLI_TruePosRate= TruePosRate;
        perf_stats(out_loc).CLI_FalsePosRate= FalsePosRate;
        perf_stats(out_loc).AUC= roc_area;
        perf_stats(out_loc).f_stat= maxFmeas;
        %perf_stats(out_loc).conf_detROC(cli)= det(squeeze(perf_stats(out_loc).Norm_conf_matROC(cli,:,:))); %close to one is better
        %perf_stats(out_loc).conf_detPR(cli)= det(squeeze(perf_stats(out_loc).Norm_conf_matPR(cli,:,:))); %close to one is better
        %perf_stats(out_loc).conf_detALL(cli)= det(squeeze(perf_stats.Norm_conf_matALL(cli,:,:))); %close to one is better
        
        if(length(cur_cl_loc)==1 && isfield(perf_stats(cur_cl_loc(1)),'labelMat'))
            %Calculate mean average precision
            cur_labelMat= vertcat(perf_stats(cur_cl_loc).labelMat);
            [recallProb,recallI]= sort(cur_labelMat(:,1),'descend');
            sort_labelMat= cur_labelMat(recallI,:);
            
            nonzero_locs= find(recallProb>0);%1:length(recallProb);%find(recallProb>0);
            avgPrec= cumsum(sort_labelMat(nonzero_locs,2)==1)./[1:length(sort_labelMat(nonzero_locs,1))]';%is actually Precision at each cutoff
            
            valid_P_locs= find(sort_labelMat(nonzero_locs,2)==1);
            num_cur_CL= length(find(sort_labelMat(:,2)==1));
            meanAP= sum(avgPrec(valid_P_locs))/num_cur_CL;%average precision
            ranked_prec= avgPrec(valid_P_locs);
        else
            meanAP= -1;
            ranked_prec= -1;
        end
        perf_stats(out_loc).meanAP= meanAP;
        perf_stats(out_loc).ranked_Precision= ranked_prec;
        
        if(f_plot)
            figure(fig1);%, hold on
            %set(gcf,'name',['Class Id:' num2str(unq_classes(cur_cl_loc(1))') ' NumEx:' num2str(length(cur_cl_loc))]);
            set(gcf,'name',['Class Id:' num2str(unq_classes(cli)') ' NumEx:' num2str(length(cur_cl_loc))]);
            %cl_colors= colormap(lines);
            subplot(1,2,1),hold on, %grid on %ROC curve
            if(isfield(perf_stats(cur_cl_loc),'FA_area_norm'))
                xlabel('False Alarms/10km^2-area','fontsize',14)
            else
                xlabel('False Positive Rate','fontsize',14)
            end
            ylabel('True Positive Rate','fontsize',14)
            title([gsd_str ' ROC Curve'],'fontsize',14)
            set(gca,'fontsize',14)
            
            subplot(1,2,2),hold on, %grid on %PR curve,
            xlabel('Recall','fontsize',14)
            ylabel('Precision','fontsize',14)
            title([gsd_str 'PR Curve'],'fontsize',14)
            set(gca,'fontsize',14)
            
            clear leg_str
            subplot(1,2,1)
            %plot(perf_stats.FalsePosRate(:,cli),perf_stats.TruePosRate(:,cli),'color',cl_colors(cli,:),'linewidth',3)
            plot([FalsePosRate],[TruePosRate],'color',cl_colors(out_loc,:),'linewidth',3)
            
            leg_str1{cli}= [' Area=' num2str(roc_area)];
            
            subplot(1,2,2)
            %plot(Recall,Precision,'color',[0 0 1],'linewidth',3)
            plot([Recall],[Precision],'color',cl_colors(out_loc,:),'linewidth',3)
            %plot3(TN_rate,Precision,perf_stats.th_range,'color',[0 0 1],'linewidth',3)
            
            leg_str2{cli}= ['Class ' num2str(out_loc)];
            
            subplot(1,2,1), %legend(leg_str1);
            subplot(1,2,2), %legend(leg_str2);
            %plot([0 1],[1 1]* tpfn_denom(1)/length(perf_stats(1).th_range),'k--'), axis square
            if(0)
                figure(fig2)
                subplot(1,2,1), hold on
                xlabel('Threshold','fontsize',14)
                ylabel('SA','fontsize',14)
                title([gsd_str 'Segmentation Accuracy'],'fontsize',14)
                set(gca,'fontsize',14)
                plot(thresh1,perf_stats(out_loc).segemtnation_accuracy_meas,'color',cl_colors(out_loc,:),'linewidth',3)
                
                subplot(1,2,2), hold on
                xlabel('Threshold','fontsize',14)
                ylabel('Accuracy','fontsize',14)
                title([gsd_str 'Overall Accuracy'],'fontsize',14)
                set(gca,'fontsize',14)
                plot(thresh1,perf_stats(out_loc).accuracy_meas,'color',cl_colors(out_loc,:),'linewidth',3)
            end
        end
    end
end
if(f_plot && 0)
    if(~isfield(perf_stats(cur_cl_loc(1)),'FA_area_norm'))
        figure(fig1)
        subplot(1,2,1), legend(leg_str1);
        plot([0 1],[0 1],'k--'), axis square
    end
    subplot(1,2,2), legend(leg_str2);
end

%******************************************************************************************
function roc_area= calculate_roc_area(FalsePosRate,TruePosRate)

x_range= [0 1 1 FalsePosRate' 0];
y_range= [0 0 1 TruePosRate' 0];
roc_area= polyarea(x_range,y_range);
