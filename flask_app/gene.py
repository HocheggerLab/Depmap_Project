
from flask import abort, make_response

from config import db
from models import Gene, gene_schema, genes_schema


def read_all():
    genes = Gene.query.all()
    return genes_schema.dump(genes)

def create(gene_dict):
    gene_name = gene_dict.get('GENE')
    existing_gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if existing_gene is None:
        new_gene = gene_schema.load(gene_dict, session=db.session)
        db.session.add(new_gene)
        db.session.commit()
        return gene_schema.dump(new_gene), 201
    else:
        abort(406, f"Gene with name {gene_name} already exists")

def read_one(gene_name):
    gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if gene is not None:
        return gene_schema.dump(gene)
    else:
        abort(404, f"Gene with name {gene_name} not found")

def update(gene_name, gene_dict):
    existing_gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if existing_gene:
        update_gene = gene_schema.load(gene_dict, session=db.session)
        for key, value in update_gene.items():
            setattr(existing_gene, key, value)
        db.session.merge(existing_gene)
        db.session.commit()
        return gene_schema.dump(existing_gene), 201
    else:
        abort(404, f"Gene with name {gene_name} not found")

def delete(gene_name):
    existing_gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if existing_gene:
        db.session.delete(existing_gene)
        db.session.commit()
        return make_response(f"{gene_name} successfully deleted", 200)
    else:
        abort(404, f"Gene with name {gene_name} not found")
