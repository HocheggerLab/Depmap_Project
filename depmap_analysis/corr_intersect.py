import pandas as pd
import numpy as np
from scipy import stats


def pearson(df, Gene):
    """
    Return a dict with Gene name, PearsonR and p-value, comparing Gene with all genes in df
    """
    dict1 = {'Gene': [], 'Pearson_R': [], 'Pearson_p': []}
    for col in df:
        (P, p) = stats.pearsonr(df[Gene].astype(np.float64), df[col].astype(np.float64))
        dict1['Gene'].append(col)
        dict1['Pearson_R'].append(P)
        dict1['Pearson_p'].append(p)
    df_R = pd.DataFrame.from_dict(dict1)
    df_R = df_R.sort_values('Pearson_p')
    df_R.reset_index(drop=True)
    return df_R


def spearman(df, Gene):
    """
    Return a dict with Gene name, Spearman R and p-value, comparing Gene with all genes in df
    """
    dict1 = {'Gene': [], 'Spearman_R': [], 'Spearman_p': []}
    for col in df:
        (P, p) = stats.spearmanr(df[Gene], df[col])
        dict1['Gene'].append(col)
        dict1['Spearman_R'].append(P)
        dict1['Spearman_p'].append(p)
    df_R = pd.DataFrame.from_dict(dict1)
    df_R = df_R.sort_values('Spearman_p')
    df_R.reset_index(drop=True)
    return df_R


def diff_means(df, Gene):
    """
    Cell Filtering. Defining Gene of interest and identifying the most sensitive and resistant cells in the CERES and
    Achilles gene dependency data sets. Returns CSV files and Figure for MASTL dependencies.
    """
    # Select Achilles data on GOI
    df1 = df.loc[:, Gene]
    df1 = df1.to_frame().reset_index()
    df1.columns = ['CCLE Name', 'gene_dep_score']
    df1 = df1.sort_values(by='gene_dep_score')
    df_res = df1.iloc[-50:]
    df_sen = df1.iloc[:50]
    df = df.reset_index()
    df['sensitive'] = df['CCLE_Name'].isin(df_sen['CCLE Name']).astype(np.int8)
    df['resistant'] = df['CCLE_Name'].isin(df_res['CCLE Name']).astype(np.int8)
    # Compute the difference of means: diff_means_exp
    diff_mean = df[df['resistant'] == 1].iloc[:, 1:-2].mean() - df[df['sensitive'] == 1].iloc[:, 1:-2].mean()
    diff_mean = pd.DataFrame(diff_mean)
    diff_mean.columns = ['Mean_Diff']
    diff_mean.index.name = 'Gene'
    t, p = stats.ttest_ind(df[df['sensitive'] == 1].iloc[:, 1:-2], df[df['resistant'] == 1].iloc[:, 1:-2],
                           nan_policy='omit')
    diff_mean['Mean_Diff_p'] = p
    diff_mean = diff_mean.sort_values('Mean_Diff_p')
    diff_mean = diff_mean.reset_index()
    return diff_mean

def common_key(a, b, c):
    """
    takes three dictionaries a,b,c  and returns  key value pairs
    of a that are also in b and c
    """
    list1 = []
    for i in a.keys():
        for j in b.keys():
            list1.extend(i for k in c.keys() if i == j == k)
    return {k: [a[k], b[k], c[k]] for k in list1}


def intersect(df, Gene):
    df_corr = pd.DataFrame()
    # Collect Data for Pearson_R
    df_R = pearson(df, Gene)
    df_R = df_R.sort_values(by='Pearson_p')
    df_R = df_R.reset_index(drop=True)

    # Collect Data for Spearman_R
    df_S = spearman(df, Gene)
    df_S = df_S.sort_values(by='Spearman_p')
    df_S = df_S.reset_index(drop=True)

    # Collect Data for Difference of Means
    df_dm = diff_means(df, Gene)

    # Merge Pearson and DM
    df_merge1 = pd.concat([df_R.iloc[0:400, :], df_S.iloc[0:400, :]], axis=1)
    df_merge2 = pd.concat([df_merge1, df_dm.iloc[0:400, :]], axis=1)
    df_merge2.columns = ['Gene_P', 'Pearson_R ', 'Pearson_p', 'Gene_S',
                         'Spearman_R ', 'Spearman_p', 'Gene_MD', 'Mean_Diff', 'Mean_Diff_p']

    # Get overlap
    P_dict = dict(zip(df_merge2['Gene_P'], df_merge2['Pearson_R ']))
    S_dict = dict(zip(df_merge2['Gene_S'], df_merge2['Spearman_R ']))
    MD_dict = dict(zip(df_merge2['Gene_MD'], df_merge2['Mean_Diff']))
    dict_all = common_key(P_dict, S_dict, MD_dict)
    df_all = pd.DataFrame.from_dict(dict_all, orient='index', dtype=None)
    df_all = df_all.reset_index()
    df_all.columns = [Gene + '_Correlations', Gene + '_Pearson_R', Gene + '_Spearman_R', Gene + '_Mean_Diff']
    df_all[Gene + '_Pearson_p'] = df_merge2['Pearson_p']
    df_all[Gene + '_Spearman_p'] = df_merge2['Spearman_p']
    df_all[Gene + '_Mean_Diff_p'] = df_merge2['Mean_Diff_p']
    return pd.concat([df_corr, df_all.iloc[0:100, :]], axis=1)

