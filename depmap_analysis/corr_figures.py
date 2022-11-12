import matplotlib.pyplot as plt
from depmap_analysis.corr_intersect import pearson
import matplotlib
# matplotlib.use('TkAgg')
import seaborn as sns



def save_fig(path, fig_id, tight_layout=True, fig_extension="pdf", resolution=300):
    print("Saving figure", fig_id)
    print("------------------------------------------")
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path / f"{fig_id}.{fig_extension}", format=fig_extension, dpi=resolution)


def scatterplot(path, df, df_corr):
    gene_01 = df_corr.iloc[0, 0]
    gene_02 = df_corr.iloc[1, 0]
    gene_03 = df_corr.iloc[2, 0]
    corr_01 = round(df_corr.iloc[1, 1],2)
    corr_02 = round(df_corr.iloc[2, 1],2)


    with plt.style.context('depmap_analysis/HHlab_style01.mplstyle'):
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        ax[0].scatter(x=df[gene_01], y=df[gene_02], c=colors[0], marker='.')
        ax[0].set_title(f'{gene_01} and {gene_02} correlations, r = {corr_01}', loc='left')
        ax[0].set(xlabel=f'{gene_01} CERES scores', ylabel=f'{gene_02} CERES scores')
        ax[1].scatter(x=df[gene_01], y=df[gene_03], c=colors[1], marker='.')
        ax[1].set_title(f'{gene_01} and {gene_03} correlations, r = {corr_02}', loc='left')
        ax[1].set(xlabel=f'{gene_01} CERES scores', ylabel=f'{gene_03} CERES scores')
    save_fig(path, f"{gene_01}_scatterplot")
    return


def lineplot(path, df, gene):
    """
    Generate Lineplot of Genes, vs Pearson Correlations, annotate
    highest and lowest Gene)
    """
    with plt.style.context('depmap_analysis/HHlab_style01.mplstyle'):
        fig, ax = plt.subplots(ncols=1)
        df_r = pearson(df, gene).sort_values('Pearson_R').iloc[:-1, :].reset_index()
        ax.plot(df_r['Gene'], df_r['Pearson_R'])
        plt.title(f"Pearson Correlations for {gene}")
        plt.annotate(xy=[1000, df_r.iloc[0, 2]], text=df_r.iloc[0, 1])
        plt.annotate(xy=[15000, df_r.iloc[-1, 2] - 0.05], text=df_r.iloc[-1, 1])
        plt.xlabel("Genes")
        plt.ylabel("Pearson Correlation")
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
    save_fig(path, f"{gene}_lineplot")
    return

if __name__ == "__main__":
    print('Run Program')
