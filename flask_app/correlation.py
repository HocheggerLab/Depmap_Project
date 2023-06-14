
from flask import abort, make_response

from config import db
from models import Gene, Correlation, gene_schema, genes_schema, correlation_schema


def read_correlations(gene_name):
    gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    if gene is not None:
        correlations = Correlation.query.filter(Correlation.gene == gene).all()
        return correlation_schema.dump(correlations)
    else:
        abort(404, f"Gene with name {gene_name} not found")

def update_for_gene(gene_name, correlation_id, correlation_dict):
    # Fetch the gene by name
    gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    # If gene doesn't exist, abort
    if gene is None:
        abort(404, f"Gene with name {gene_name} not found")

    # Fetch the correlation from the gene's correlations by id
    correlation = [c for c in gene.correlations if c.id == correlation_id]

    # If correlation doesn't exist, abort
    if not correlation:
        abort(404, f"Correlation with id {correlation_id} not found for gene {gene_name}")
    else:
        correlation = correlation[0]  # Extract correlation from list

    # Load the correlation_dict into a Correlation object
    updated_correlation = correlation_schema.load(correlation_dict, session=db.session)

    # Update correlation fields
    for key, value in updated_correlation.items():
        setattr(correlation, key, value)

    # Merge and commit changes to db
    db.session.merge(correlation)
    db.session.commit()

    # Return the updated correlation
    return correlation_schema.dump(correlation), 200

def create_for_gene(gene_name, correlation_dict):
    # Fetch the gene by name
    gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    # If gene doesn't exist, abort
    if gene is None:
        abort(404, f"Gene with name {gene_name} not found")

    # Create a new correlation from the given dictionary
    new_correlation = correlation_schema.load(correlation_dict, session=db.session)

    # Add the new correlation to the gene's correlations
    gene.correlations.append(new_correlation)

    # Add and commit the changes to the database
    db.session.add(new_correlation)
    db.session.commit()

    # Return the newly created correlation
    return correlation_schema.dump(new_correlation), 201

def delete_for_gene(gene_name, correlation_id):
    # Fetch the gene by name
    gene = Gene.query.filter(Gene.gene == gene_name).one_or_none()

    # If gene doesn't exist, abort
    if gene is None:
        abort(404, f"Gene with name {gene_name} not found")

    # Fetch the correlation from the gene's correlations by id
    correlation = [c for c in gene.correlations if c.id == correlation_id]

    # If correlation doesn't exist, abort
    if not correlation:
        abort(404, f"Correlation with id {correlation_id} not found for gene {gene_name}")
    else:
        correlation = correlation[0]  # Extract correlation from list

    # Delete the correlation
    db.session.delete(correlation)
    db.session.commit()

    # Return success message
    return {"message": f"Successfully deleted correlation with id {correlation_id} for gene {gene_name}"}, 200
