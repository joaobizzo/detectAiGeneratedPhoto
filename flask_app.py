from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from main import query

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['DROPZONE_TIMEOUT'] = 5 * 60 * 1000

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Submit")


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        print("File uploaded successfully")
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        filename = secure_filename(file.filename)
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename)

        if filename.split('.')[-1] in ['jpg', 'jpeg', 'png']:
            try:
                response = query(file_path)
                print(response)
                # Verificar se há um erro na resposta
                if 'error' in response:
                    error_message = response.get('error')
                    estimated_time = 10 #response.get('estimated_time', 10)
                    flash(f'API starting... try again in {int(estimated_time)} seconds.', 'info')
                    return render_template('home.html', form=form)
                # Continuar processamento se não houver erro
                max_response = max(response, key=lambda x: x['score'])
                artificial = 'true' if max_response['label'] == 'artificial' else 'false'
                score = str(max_response['score']*100)
                print(artificial, score)
                return redirect(url_for('response', artificial=artificial, score=score))
            except Exception as e:
                # Tratar qualquer outro tipo de erro
                flash(f'Erro ao processar o arquivo: {str(e)}', 'error')
                return render_template('home.html', form=form)
        else:
            flash('Formato de arquivo não suportado. Por favor, envie um arquivo .jpg, .jpeg ou .png.', 'error')
            return render_template('home.html', form=form)
        
    return render_template('home.html', form=form)


@app.route('/response/<artificial>/<score>', methods=['GET'])
def response(artificial, score):
    artificial = artificial.lower() == 'true'
    try:
        score_float = float(score)
        score_text = f"{score_float:.2f}%"
    except ValueError:
        score_text = "N/A"

    if artificial:
        response_text = 'AI generated'
        response_class = 'ai'
    else:
        response_text = 'not AI generated'
        response_class = 'not-ai'
    
    return render_template('response.html', response=response_text, response_class=response_class, score_text=score_text)




if __name__ == '__main__':
    app.run(debug=True)
