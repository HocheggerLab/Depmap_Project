from depmap_analysis.corr_intersect import pearson,spearman,diff_means,common_key
import pandas as pd
from pathlib import Path
from scipy import stats
from scipy.stats import ConstantInputWarning

import numpy as np
import warnings

def align_dataframes_on_modelID(df1, df2):
    common_modelIDs = set(df1['ModelID']).intersection(df2['ModelID'])
    df1_sync = df1[df1['ModelID'].isin(common_modelIDs)]
    df2_sync = df2[df2['ModelID'].isin(common_modelIDs)]
    # Set 'CCLE_Name' as index
    df1_sync.set_index('ModelID', inplace=True)
    df2_sync.set_index('ModelID', inplace=True)
    return df1_sync, df2_sync


def pearson_dep(df_exp,df_dep,Gene):
    """
    Return a dict with Gene name, PearsonR and p-value, comparing Gene with all genes in df
    """
    dict1 = {'Gene': [], 'Pearson_R': [], 'Pearson_p': []}
    for col in df_exp:
        if col=='ModelID':
            continue
        else:
            # Ignore warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=ConstantInputWarning)
                (P, p) = stats.pearsonr(df_dep[Gene].astype(np.float64), df_exp[col].astype(np.float64))
                dict1['Gene'].append(col)
                dict1['Pearson_R'].append(P)
                dict1['Pearson_p'].append(p)
    df_R = pd.DataFrame.from_dict(dict1)
    df_R = df_R.sort_values('Pearson_p')
    df_R.reset_index(drop=True)
    return df_R
def spearman_dep(df_exp,df_dep,Gene):
    """
    Return a dict with Gene name, Spearman R and p-value, comparing Gene with all genes in df
    """
    dict1 = {'Gene': [], 'Spearman_R': [], 'Spearman_p': []}
    for col in df_exp:
        if col == 'ModelID':
            continue
        else:
            (P, p) = stats.spearmanr(df_dep[Gene].astype(np.float64), df_exp[col].astype(np.float64))
            dict1['Gene'].append(col)
            dict1['Spearman_R'].append(P)
            dict1['Spearman_p'].append(p)
    df_R = pd.DataFrame.from_dict(dict1)
    df_R = df_R.sort_values('Spearman_p')
    df_R.reset_index(drop=True)
    return df_R


def diff_means_corr(df_exp,df_dep, Gene):
    """
    Cell Filtering. Defining Gene of interest and identifying the most sensitive and resistant cells in the CERES and
    Achilles gene dependency data sets. Returns CSV files and Figure for MASTL dependencies.
    """
    # Select Achilles data on GOI
    df1=df_dep.loc[:,Gene]
    df1 = df1.to_frame().reset_index()
    df1.columns = ['ModelID', 'gene_corr_score']
    df1 = df1.sort_values(by='gene_corr_score')
    df_res = df1.iloc[-50:]
    df_sen = df1.iloc[:50]
    df = df_exp.reset_index()
    df['sensitive'] = df['ModelID'].isin(df_sen['ModelID']).astype(np.int8)
    df['resistant'] = df['ModelID'].isin(df_res['ModelID']).astype(np.int8)
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



def intersect_corr(df_exp,df_dep, Gene):
    df_corr = pd.DataFrame()
    # Collect Data for Pearson_R
    df_R = pearson_dep(df_exp, df_dep,Gene)
    df_R = df_R.sort_values(by='Pearson_p')
    df_R = df_R.reset_index(drop=True)

    # Collect Data for Spearman_R
    df_S = spearman_dep( df_exp,df_dep,Gene)
    df_S = df_S.sort_values(by='Spearman_p')
    df_S = df_S.reset_index(drop=True)

    # Collect Data for Difference of Means
    df_dm = diff_means_corr(df_exp, df_dep,Gene)

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

if __name__=="__main__":
    dependency_data = pd.read_csv('/Users/haoranyue/Downloads/CRISPRGeneEffect.csv')
    expression_data = pd.read_csv('/Users/haoranyue/Downloads/OmicsExpressionProteinCodingGenesTPMLogp1.csv')
    expression_data = expression_data.rename(columns={expression_data.columns[0]: 'ModelID'})
    dependency_data.columns = dependency_data.columns.str.replace(r' \(\d+\)', '', regex=True)
    expression_data.columns = expression_data.columns.str.replace(r' \(\d+\)', '', regex=True)
    dependency_data,expression_data=align_dataframes_on_modelID(dependency_data,expression_data)
    depmap_data = '/Users/haoranyue/Desktop'
    gene_list=['A1CF']
    for gene in gene_list:
        path = Path(depmap_data) / f'{gene}_data'
        path.mkdir(exist_ok=True)
    df_corr = intersect_corr(expression_data,dependency_data,gene_list[0])
    df_corr.to_csv(f'{path}/{gene}_data.csv')
