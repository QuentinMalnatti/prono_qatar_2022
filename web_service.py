from flask import Flask, render_template, current_app, request
from ETL.compute import Compute

app = Flask(__name__)
with app.app_context():
    current_app.config["compute"] = Compute()


@app.route('/')
def compute_ranking():
    data = current_app.config["compute"].compute_ranking()
    return render_template('ranking.html',
                           first=current_app.config["compute"].get_rank(data, 0),
                           second=current_app.config["compute"].get_rank(data, 1),
                           third=current_app.config["compute"].get_rank(data, 2),
                           others=current_app.config["compute"].get_rank(data, 3, True))


@app.route('/prono')
def display_prono():
    return render_template('prono.html',
                           data=current_app.config["compute"].create_prono_display(),
                           res=current_app.config["compute"].create_res_display())


@app.route('/match_res')
def create_match_list():
    return render_template('match_res.html',
                           matches=current_app.config["compute"].get_matches(),
                           res=current_app.config["compute"].create_res_display())


@app.route('/match_res', methods=['POST'])
def set_match_res():
    if request.method == 'POST':
        match_info = request.form.to_dict()
        current_app.config["compute"].set_match_res(match_info)
        current_app.config["compute"].load_res()
        return render_template('match_res.html',
                               matches=current_app.config["compute"].get_matches(),
                               res=current_app.config["compute"].create_res_display())


if __name__ == "__main__":
    app.run()
