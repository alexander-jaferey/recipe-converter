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

units = {
    "gram":  ["gram ", "g ", "gr ", "gs ", "grs ", "grams "],
    "kg": ["kg ", "kgs ", "kilogram ", "kilograms "],
    "liter": ["liter ", "l ", "liters ", "litre ", "litres "],
    "ml": ["ml ", "milliliter ", "milliliters ", "millilitre ", "millilitres "]
}

convert = {
    "gram": (0.0353, "oz"),
    "kg": (2.204, "lbs"),
    "liter": (4.227, "cups"),
    "ml": (0.203, "tsps")
}

def check_for_unit(ingredient, unit):
    for abbr in unit:
        if abbr in ingredient:
            i = ingredient.find(abbr)
            if ingredient[i - 1].isdigit():
                return (i - 1, unit[0])
            elif ingredient[i - 1] == " ":
                if ingredient[i - 2].isdigit():
                    return (i - 2, unit[0])

def convert(ingredient, index, abbr):
    i = index
    while True:
        if ingredient[i].isdigit() is False:
            break
        else: i -= 1
    try:
        m_amt = float(ingredient[i:(index + 1)])
    except:
        m_amt = 0
    cust_amt = m_amt * convert[abbr][0]
    return (cust_amt, abbr)



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

        ingr = img_txt.split("\n")

        ing_num = 0
        for ing in ingr:
            for unit in units.values():
                if check_for_unit(ing, unit):
                    ing_num += 1
                    print(ing)

        print(ing_num)

        return render_template('index.html', form=form, text=img_txt)

    return render_template('index.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        app.debug = True
        app.run()