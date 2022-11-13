Latest Version of DepMap Correlation Analysis Nov 2022

A simple workflow to analyse DepMap dependencies and analyse the
top 100 correlations using string and network analysis.

To start you need to import the latest DepMap release data,
https://depmap.org/portal/download/all/
Run the DataImport.py file.
This will generate a AnalysisData folder with the
cleaned up CRIPSR gene effect data as a csv file.

In the main.py file add the gene or genes that you interested
in as strings in the list called gene_list.
The program generates 1) figures showing Pearson Correlations
for the top two corrleating genes, 2) a csv file with the top
100 correlating genes from an intersection (Pearson, Spearman, Mean_Diff)
and info on the correlation coeff, the group of genes belonging to the largest
clique community based on the string network and the GO pathways
enriched in this group; 3) A Figure with the string network. We use the
default values from teh String API.



