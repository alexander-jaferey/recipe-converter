import os
import secrets

from PIL import Image
import pytesseract

from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'])])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PhotoForm()

    if form.validate_on_submit():
        # delete previous images in image directory
        for item in os.listdir(f"{app.root_path}/images"):
            if item != 'sample-image.png':
                os.remove(f"{app.root_path}/images/{item}")

        f = form.photo.data
        img_txt = pytesseract.image_to_string(Image.open(f))

        return render_template('index.html', form=form, text=img_txt)

    return render_template('index.html', form=form)




if __name__ == '__main__':
    with app.app_context():
        app.debug = True
        app.run()
