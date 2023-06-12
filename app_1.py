from flask import Flask, request, redirect, url_for, flash, send_from_directory,render_template
import zipfile
from depmap_analysis import corr_figures, corr_intersect, corr_network
import pandas as pd
from io import StringIO
from pathlib import Path
import os
from flask import send_file
import logging
import connexion

app= connexion.App(__name__,specification_dir='./')
app.add_api('swagger.yml')

@app.route('/')
def home()
    return render_template('home.html')

ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
# get the absolute path of the current script file
dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

# join the script directory with the 'static/result_data' subdirectory
path = dir_path / 'static' / 'result_data'

# now use result_data_path instead of 'static/result_data'
path.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/start_analysis', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # get gene list from form input, splitting on commas
        gene_list = request.form['genes'].split(',')

        file = request.files['file']
        if file and allowed_file(file.filename):
            # we don't save the file, instead we read it directly into a DataFrame
            df = pd.read_csv(StringIO(file.read().decode('utf-8')),index_col=0)

            pearson_analysis(df, gene_list)
            flash('File uploaded and processed successfully')
            return redirect(url_for('upload_file'))  # redirect back to the upload page

    # display the upload form
    return render_template('home.html')

@app.route('/download_results')
def download_results():
    # Create a ZipFile object
    zip_path = dir_path / 'static'/'result_data.zip'
    try:
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for foldername, subfolders, filenames in os.walk(str(dir_path)+"/static"):
                for filename in filenames:
                    if filename == '.DS_Store':
                        continue  # skip this file
                    # create complete filepath of file in directory
                    file_path = Path(foldername) / filename
                    # add file to zip
                    zip_file.write(file_path, arcname=os.path.basename(file_path))  # Use basename to exclude directory structure
    except Exception as e:
        logging.error("An error occurred while creating the zip file:", exc_info=True)
        return "An error occurred while creating the zip file: " + str(e), 500

    return send_file(zip_path, as_attachment=True, mimetype='application/zip')



def pearson_analysis(df, gene_list):
    for gene in gene_list:
        df_corr = corr_intersect.intersect(df, gene.strip())  # strip whitespace from gene name
        corr_figures.scatterplot(path, df, df_corr)
        corr_figures.lineplot(path, df, gene.strip())
        corr_network.save_network_go(path, df_corr, gene.strip())

if __name__ == '__main__':
    app.secret_key = 'some secret key'
    app.run(debug=True)
    # download_results()
