% ckwg +5
% Copyright 2013 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


%Purpose: Read a .txt file into an array of cells filled with strings of each row of the .txt file
%This version ends the line scanning when a -1 is returned (allows blank lines in file)

function txtfile= read_file_into_cellofstrings_v2(PathName, fileName)

clear txtfile
if(~isempty(fileName))
    fp = fopen([PathName filesep fileName],'r');
else
    fp = fopen([PathName],'r');
end

if(fp~=-1)
    FlineNum= 1;
    while(1)
        %txtfile{FlineNum}= fscanf(fp,'%s',1);
        
        txtfile{FlineNum} = fgetl(fp);
        if(txtfile{FlineNum}==-1)
            txtfile(FlineNum)= [];
            break
        end
        
        FlineNum= FlineNum+1;
    end
    fclose(fp);
    fclose all;
else
   txtfile= {}; 
end

