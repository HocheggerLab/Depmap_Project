from datetime import datetime

from config import app, db
from models import Note, Gene

GENE_CORRELATION=[
    {'GENE':"MASTL",
     'Corr_GENE':'PPP2CA',
     'Pearson_R': 1.00,
     'Spearman_R':1.0,
     "Mean_Diff":1.70257741016433,
     'Pearson_p':0.0,
     'Spearman_p':0.0,
     'Mean_Diff_p':2.86501942077693E-63,
     'Largest_Comm': False,
     'type':'DNA replication',
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
        new_gene = Gene(gene=data.get("GENE"), corr_gene=data.get("Corr_GENE"),
                        pearson_r=data.get("Pearson_R"), spearman_r=data.get("Spearman_R"),
                        mean_diff=data.get("Mean_Diff"), pearson_p=data.get("Pearson_p"),
                        spearman_p=data.get("Spearman_p"), mean_diff_p=data.get("Mean_Diff_p"),
                        largest_comm=data.get("Largest_Comm"), type=data.get("type"))
        for content, timestamp in data.get("notes", []):
            new_gene.notes.append(
                Note(
                    content=content,
                    timestamp=datetime.strptime(
                        timestamp, "%Y-%m-%d %H:%M:%S"
                    ),
                )
            )
        db.session.add(new_gene)
    db.session.commit()

