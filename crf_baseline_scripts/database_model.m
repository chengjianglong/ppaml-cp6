% ckwg +5
% Copyright 2015 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


function model = database_model(ly, lx, nvals, cliq_mat)

N = reshape(1:ly*lx,ly,lx);

model.nnodes    = lx;
model.nodetype  = ones(lx,1);
model.nodewhere = 1:lx;

model.ncliques = lx;
model.nvals    = nvals;
model.pairtype = [];%zeros(model.ncliques,1);

model.pairs     = [];%zeros(model.ncliques,2);
model.modeltype = 'mcl_cliques';%'maxclique'; %!!! Not sure if this label is used for anything in the code...
model.treenum   = [];%zeros(model.ncliques,1);
model.ly = ly;
model.lx = lx;

%model.tree2clique = zeros(max(ly-1,lx-1),lx+ly);

model.tree2clique = zeros(1,lx);

pair_cnt=1;
for(imi=1:lx)    
    imi_cliq_locs= find(cliq_mat(imi,:));
    for(imi2=1:length(imi_cliq_locs))
        if(imi ~= imi_cliq_locs(imi2))
            if(pair_cnt>1)
                curp_locs= find(model.pairs(:,1)==imi & model.pairs(:,2)==imi_cliq_locs(imi2));
                curp2_locs= find(model.pairs(:,2)==imi & model.pairs(:,1)==imi_cliq_locs(imi2));
            else
                curp_locs = [];
                curp2_locs= [];
            end
            
            if(isempty(curp_locs) && isempty(curp2_locs))
                model.pairs(pair_cnt,:)  = [imi imi_cliq_locs(imi2)];
                model.pairtype(pair_cnt,1) = 1;
                model.treenum(pair_cnt,1)  = 1;
                model.tree2clique(1,imi2) = pair_cnt;%trw_bprop_scheduled.m needs this to be the index into model.paris(pair_cnt,1)
                pair_cnt = pair_cnt+1;
            end
        end
    end
end

s_vert = size(model.tree2clique,2);%!!! This might need to be set to the number of clusters, not the total indices
model.treeschedule = [1:s_vert]'; %!!! Might need to add a second column here, but it seemed specific to separate types of clique (vertical vs horizontal), still not sure why they were separated


% compute neighborhoods
[model.N1, model.N2] = find_node2pair_arrays_ver2(model);%!!! Not sure what this is used for

