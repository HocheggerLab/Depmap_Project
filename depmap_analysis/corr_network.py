import pandas as pd
import numpy as np
import networkx as nx
import requests
import gseapy as gp
import matplotlib.pyplot as plt



def save_fig(path, fig_id, tight_layout=True, fig_extension="png", resolution=300):
    print("Saving figure", fig_id)
    print("------------------------------------------")
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path / f"{fig_id}.{fig_extension}", format=fig_extension, dpi=resolution)

def generate_network(gene_list):
    """
    Connect to String get network data nd store in pandas dataframe
    :param gene_list: gene list from IS.csv file
    :return: dataframe with neywork data
    """
    string_api_url = "https://string-db.org/api"
    output_format = "tsv-no-header"
    method = "network"

    # Construct URL

    request_url = "/".join([string_api_url, output_format, method])

    # Set parameters

    params = {
        "identifiers": "%0d".join(gene_list),  # your protein
        "species": 9606,  # species NCBI identifier
        "caller_identity": "http://www.sussex.ac.uk/lifesci/hocheggerlab/",  # lab homepage
        "add_nodes": 0
    }
    # Call STRING
    r = requests.post(request_url, data=params)

    # re-format r as pandas dataframe
    cols = ['stringId_A', 'stringId_B', 'preferredName_A', 'preferredName_B', 'ncbiTaxonId', 'score', 'nscore',
            'fscore', 'pscore', 'ascore', 'escore', 'dscore', 'tscore']
    lines = r.text.split('\n')  # pull the text from the response object and split based on new lines
    data = [l.split('\t') for l in lines]  # split each line into its components based on tabs
    # convert to dataframe using the first row as the column names; drop empty, final row
    df = pd.DataFrame(data[1:-1], columns=cols)
    # Add unconnected nodes from original list
    for entry in gene_list:
        if entry not in df['preferredName_A']:
            df.loc[len(df.index)] = ['NaN', 'NaN', entry, entry, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                                     'NaN']
    # dataframe with the preferred names of the two proteins and the score of the interaction
    return df[['preferredName_A', 'preferredName_B', 'score']]


def Network_import(df):
    """
    Imports df from String function into NetworkX with edge assigned
    a string score
    :param df dataframe returned from generate_network function
    :return: A network file
    """
    G = nx.Graph(name='Protein Interaction Graph')
    interactions = np.array(df)
    for i in range(len(interactions)):
        interaction = interactions[i]
        a = interaction[0]  # protein a node
        b = interaction[1]  # protein b node
        w = float(interaction[2])  # score as weighted edge where high scores = low weight
        G.add_weighted_edges_from([(a, b, w)])  # add weighted edge to graph
    return G


def community_go(G, gene):
    """
    Selects largest 3-clique community from G
    and performs GSEA with this list (if the community contains 6 or more genes)
    """
    df_go = pd.DataFrame()
    com = sorted(nx.algorithms.community.k_clique_communities(G, 3), key=lambda x: len(x))
    if list(com):
        gene_list = list(list(com)[-1])
        if len(gene_list) >= 6:
            enr = gp.enrichr(gene_list=gene_list, gene_sets=['KEGG_2021_Human', 'GO_Biological_Process_2021'],
                             organism='Human', cutoff=0.5)

            df = enr.results
            if len(df) > 0:
                df_go = pd.concat([df_go, df['Term']], axis=1).rename(columns={"Term": gene})
            else:
                print('no GO enrichment')
        else:
            print('clique community too small')
        return com, df, df_go

def network_figure(path, G, gene):

    pos=nx.spring_layout(G, k=1, iterations=100)


    with plt.style.context("dark_background"):
        fig1, ax1 = plt.subplots(ncols=1, figsize=(11, 11))
        nx.draw_networkx(G, pos=pos, with_labels=True, node_color=range(len(G)), cmap='Dark2', node_size=1000,edge_color= 'white', width=2,
                         font_color='white',font_weight='bold',font_size='7', ax=ax1)
        plt.axis('off')
    save_fig(path, gene+'_Network')
    return



def save_network_go(path, df, gene):
    interactions = generate_network(df.iloc[:, 0].to_list())
    G = Network_import(interactions)
    G.remove_edges_from(nx.selfloop_edges(G))
    print(f"Saving {gene} Correlation Network")
    print("------------------------------------------")
    nx.write_graphml(G, path / f"{gene}_corr.graphml")
    community, df_GSAE, df_GO = community_go(G, gene)
    df['Largest_Comm'] = df[f'{gene}_Correlations'].isin(list(list(community)[-1]))
    df_final = pd.concat([df, df_GO], axis=1)
    df_final.to_csv(path / f"{gene}_corr.csv")
    network_figure(path, G, gene)

