from flask import Flask, render_template, current_app
from ETL.compute import Compute

app = Flask(__name__)
with app.app_context():
    current_app.config["compute"] = Compute()


@app.route('/')
def compute_ranking():
    return render_template('ranking.html', data=current_app.config["compute"].compute_ranking())


@app.route('/prono')
def display_prono():
    return render_template('prono.html',
                           data=current_app.config["compute"].create_prono_display(),
                           res=current_app.config["compute"].create_res_display())


if __name__ == "__main__":
    app.run()
