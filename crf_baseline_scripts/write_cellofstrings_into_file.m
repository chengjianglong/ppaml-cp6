% ckwg +5
% Copyright 2011-2013 by Kitware, Inc. All Rights Reserved. Please refer to
% KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
% Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


%Purpose: 
function write_cellofstrings_into_file(PathName, fileName, txtfile)

if(~isempty(fileName))
    [fp,mesg]= fopen([PathName filesep fileName],'w');
else
    [fp,mesg]= fopen([PathName],'w');
end

%Place new line character at end of each cell
for(ri=1:length(txtfile))  
    fprintf(fp,'%s\n',txtfile{ri});
end

fclose(fp);
fclose all;


