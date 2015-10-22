#Instructions on how to compile and run the baseline CRF on the MIR sandbox dataset
#Contact Eran Swears with questions, eran.swears@kitware.com

The CRF baseline code uses Justin Domke's marbl toolbox to perform learning and inference of general CRFs, which are c++ executables.
Kitware wrote a Matlab wrapper (wrapper_crf_database_labeling_v2.m) around these that parse the MIR datafiles and format them into the model*.txt and data*.txt files for training and test.
The public sandbox data (2015-10-sandbox-v2/round-1-public) is separated into a local train (5216 images) and test (2252 images) set, so the CRF trains a model using the training data and evaluates it's performance using the test data.

Prerequisits:
1- Copy/move all the files in this folder into the 2015-10-sandbox-v2/round-1-public folder
2- All testing has been performed on Ubuntu machines, although compiling the MARBL c++ code on other linux machines may not have too many more challenges. I don't believe anyone has tried to compile Marbl on Windows, but if you figure it the Author of MARBL, Justin Domke, would be interested in the instructions for doing this.  
3- A Matlab license is needed to run the CRF Wrapper code, no Matlab toolboxes are needed.
4- Download a copy of the MARBL CRF toolbox from github: https://github.com/justindomke/marbl
	- Replace the learn_CRF.cpp function in the marble/main_code directory with the version that is in the 2015-10-public-sandbox directory (we added a path variable so the user can define where to write the learned weight vector)
	- Follow the "Getting Started" instructions in the README.md file.  
	- If you want parrallel processing you will need to install openMPI and openMP.

Experimental Setup:
- The CRf learning and testing follows the methods used in [1]
- Each label is processed separately through a one vs. other classifier
- Each node of the CRF represents a single image
- All of the unary and edge features are currently binary, but the origal feature spaces could be quantized to allow more granularity
- Only the 1000 top most frequent words and 1000 top most frequent groups are used in the feature space
- The training data was originally used as one large databased for training, but the Limited-memory Broyden-Fletcher-Goldfarb-Shanno (L-BFGS) optimization method does not update the parameters in this case.
	- To get around this, the training data is separated into four independent databases, which the L-BFGS algorithm is then able to use to update the CRF parameters
- Inference is performed on the entire testing database as one example
- The classification performance Matlab datastructure for each label is stored in their corresponding .../2015-10-sandbox-v2/round-1-public/runout/testing/class*/cvi1 folder, where * is replaced by the label number
- The overall classification performance datastructure is store in .../2015-10-sandbox-v2/round-1-public/runout/testing
- Classification performance is currently poor, but it may be possible to improve this by trying one or more of the following:
	- Quantize the feature space instead of using binary features
	- Removing features (words/edges) that are not very information
	- Change the hidden labels from binary (1=class of interest,0=other) so they have 25 values (one for the 24 labels and one for the "other" class)


Instructions for training and testing with CRF:
1- There are three config file parameters:
	- f_load_edges: It can take a while to extract the edge features, but these are saved afterwards, so you can set this flag to load the previously extracted edge features the next time you run the code by seeting this to 1
	- f_plot: Used for plotting ROC/PR curves, but these are not really that informative with this dataset, since there is an extremem imbalance between the number of true positives for a particular lable and the number of true negatives
	- marbl_path
2- execute the run.sh script (cd to 2015-10-public-sandbox folder and type the following in the terminal $ sh run.sh)
3- You can also run the wrapper_crf_database_labeling_v2.m directly and step into the load_files_extract_structures.m and subroutines to determine how the raw data files are parsed.
 

Troubleshooting:
1 - When running the scripts for the first time you may get a Matlab error that says something like:
	".../glnxa64/libstdc++.so.6:version 'BLIBCXX_3.4.18 not found (required by ..."
	- To solve this run the following command in the ubuntu terminal window, where you adapt versions/paths to your system:
	sudo ln -sf /usr/lib/x86_64-lsnux-gnu/libstdc++.so.6 /usr/local/MATLAB/R2015b/sys/os/glnxa64/libstdc++.so.6
		
References:
[1] Justin Domke, "Learning Graphical Model Parameters with Approximate Marginal Inference," IEEE Transactions on Pattern Analysis, 2013