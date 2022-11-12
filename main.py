from depmap_analysis import corr_figures, corr_intersect, corr_network
import pandas as pd
from pathlib import Path

gene_list = ['AURKA']

df = pd.read_csv('CRISPR_gene_effect_clean.csv', index_col=0)
depmap_data = '/Users/hh65/Documents/Current_Results'
for gene in gene_list:
    path = Path(depmap_data) / f'{gene}_data'
    path.mkdir(exist_ok=True)
    if __name__ == '__main__':
        df_corr = corr_intersect.intersect(df, gene)
        corr_figures.scatterplot(path, df, df_corr)
        corr_figures.lineplot(path, df, gene)
        corr_network.save_network_go(path, df_corr, gene)
