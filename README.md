Code relevant for Hbb.

How to run:

Go into test/:

> cd test/

Make a light skim of vhbb trees and save the output into /scratch/$USER:
Edit the list of files (path and splitting parameters in ../python/samples.py
and make sure that submit.py processes the correct samples 

> python submit.py run_tree_skimmer

Merge the trees into one tree (sustainable with current skim):

> ./mergeall.sh

Place the trees into a SE:

> ./copyToSE.sh

Produce histograms out of the skimmed trees:

> python submit.py run_histos

Move the output files into ./plots:

> mv *root .plots/

Produce histograms and total signal/background templates:

> root -b

root [0] .L make_plots.C++

root [0] plot_all()

A ROOT file with all shapes is saved under plots/plots.root
