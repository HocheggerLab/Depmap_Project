
from flask import abort, make_response

from config import db
from models import Gene, Correlation, gene_schema, genes_schema, correlation_schema



def read_all():
    genes = Gene.query.all()
    return genes_schema.dump(genes)

def read_one(gene_name):
    gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if gene is not None:
        return gene_schema.dump(gene)
    else:
        abort(404, f"Gene with name {gene_name} not found")

def create(gene_dict):
    gene_name = gene_dict.get('gene')
    existing_gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if existing_gene is None:
        new_gene = gene_schema.load(gene_dict, session=db.session)

        correlations=gene_dict.get('coorlations')
        if correlations:
            for corr in correlations:
                new_correlation = correlation_schema.load(corr, session=db.session)
                new_gene.correlations.append(new_correlation)
        db.session.add(new_gene)
        db.session.commit()
        return gene_schema.dump(new_gene), 201
    else:
        abort(406, f"Gene with name {gene_name} already exists")

def update(gene_name,gene_dict):
    existing_gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if existing_gene:
        update_geen=gene_schema.load(gene_dict,session=db.session)
        for key,value in update_geen.items():
            if key =='correlations' and value:
                existing_gene.correlations.clear()
                for corr in value:
                    new_correlation =correlation_schema.load(corr,session=db.session)
                    existing_gene.correlations.append(new_correlation)
            else:
                setattr(existing_gene,key,value)
        db.session.merge(existing_gene)
        db.session.commit()
        return gene_schema.diump(existing_gene),201
    else:
        abort(404,f' Gene with name {gene_name} not found')




def delete(gene_name):
    existing_gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if existing_gene:
        db.session.delete(existing_gene)
        db.session.commit()
        return make_response(f"{gene_name} successfully deleted", 200)
    else:
        abort(404, f"Gene with name {gene_name} not found")
