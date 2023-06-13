from datetime import datetime

from config import app, db
from models import Note, Gene, Correlation

GENE_CORRELATION=[
    {"MASTL":[{'Corr_GENE': 'PPP2CA',
               'Pearson_R': 1.00,
               'Spearman_R': 1.0,
               "Mean_Diff": 1.70257741016433,
               'Pearson_p': 0.0,
               'Spearman_p': 0.0,
               'Mean_Diff_p': 2.86501942077693E-63,
               'Largest_Comm': False,
               'type': 'DNA replication'},
              {'Corr_GENE': 'POT1',
               'Pearson_R': -0.308892030723026,
               'Spearman_R': 1.0,
               "Mean_Diff": 1.70257741016433,
               'Pearson_p': 0.0,
               'Spearman_p': 0.0,
               'Mean_Diff_p': 2.86501942077693E-63,
               'Largest_Comm': False,
               'type': 'DNA replication'}
              ],

     "notes": [
         (
             " analysis gene from Depmap_project",
             "2023-06-12 09:15:03",
         ),
     ],
     }
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for data in GENE_CORRELATION:
        gene_name = list(data.keys())[0]  # Get the gene name, it's the first key
        new_gene = Gene(gene=gene_name)  # Create a new Gene with the obtained gene name
        db.session.add(new_gene)

        for corr in data[gene_name]:  # Iterate over the correlations of the gene
            new_correlation = Correlation(
                corr_gene=corr.get("Corr_GENE"),
                pearson_r=corr.get("Pearson_R"),
                spearman_r=corr.get("Spearman_R"),
                mean_diff=corr.get("Mean_Diff"),
                pearson_p=corr.get("Pearson_p"),
                spearman_p=corr.get("Spearman_p"),
                mean_diff_p=corr.get("Mean_Diff_p"),
                largest_comm=corr.get("Largest_Comm"),
                type=corr.get("type")
            )
            db.session.add(new_correlation)
            new_gene.correlations.append(new_correlation)

        for content, timestamp in data.get("notes", []):
            new_note = Note(
                content=content,
                timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            )
            new_gene.notes.append(new_note)
            db.session.add(new_note)

    db.session.commit()
