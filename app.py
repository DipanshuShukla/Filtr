from flask import Flask, render_template, url_for, request, redirect, session, flash
from werkzeug.utils import secure_filename
from tempfile import mkdtemp
from flask_session import Session
from cs50 import SQL
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import os, requests, urllib.parse
from functools import wraps

from filter import *

app = Flask("__name__")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = SQL("sqlite:///test.db")

app.config["IMAGE_UPLOADS"] = "static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
# app.config["IMAGE SELECTED"] =

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["FILTER_NAMES"] = ["Orignal", "Country", "Crossprocess", "Desert", "Lumo", "Nashville", "Portaesque",
                              "Proviaesque",
                              "Velviaesque"]


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(
            f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def allowed_image(filename):
    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/upload-image", methods=["GET", "POST"])
@login_required
def upload_image():
    if request.method == "POST":

        if request.files:

            image = request.files["image"]

            if image.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_image(image.filename):
                filename = secure_filename(image.filename)

                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                db.execute("INSERT INTO imgs (id, image) VALUES (:id, :image)",
                           id=session.get("user_id"),
                           image=filename)

                print("Image saved")
                return redirect("/filter")

            else:
                print("That file extension is not allowed")
                return redirect(request.url)

    return render_template("/upload_image.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign inputs to variables
        input_name = request.form.get("name")
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        input_confirmation = request.form.get("confirmation")

        # Ensure name was submitted
        if not input_name:
            return apology("must provide your name", 403)

        # Ensure username was submitted
        if not input_username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not input_password:
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not input_confirmation:
            return apology("must provide password confirmation", 418)

        elif not input_password == input_confirmation:
            return apology("passwords must match", 418)

        # Query database for username
        username = db.execute("SELECT username FROM users WHERE username = :username",
                              username=input_username)

        # Ensure username is not already taken
        if len(username) == 1:
            return apology("sorry, username is already taken", 403)

        # Query database to insert new user
        else:
            new_user = db.execute("INSERT INTO users (name, username, hash) VALUES (:name, :username, :password)",
                                  name=input_name,
                                  username=input_username,
                                  password=generate_password_hash(input_password, method="pbkdf2:sha256",
                                                                  salt_length=8))

            if new_user:
                # Keep newly registered user logged in
                session["user_id"] = new_user

            # Flash info for the user
            flash(f"Registered as {input_username}")

            # Redirect user to homepage
            return redirect("/")

    # User reached route via GET (as by clicking a l</a>ink or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")

        # Ensure username was submitted
        if not input_username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not input_password:
            return apology("must provide password", 403)

        # Query database for username
        username = db.execute("SELECT * FROM users WHERE username = :username",
                              username=input_username)

        # Ensure username exists and password is correct
        if len(username) != 1 or not check_password_hash(username[0]["hash"], input_password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = username[0]["id"]

        # Flash info for the user
        flash(f"Logged in as {input_username}")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/filter", methods=["GET", "POST"])
@login_required
def filters():
    if request.method == "POST":
        print(request.form['submit_button'])
        create_filters(request.form['submit_button'])
        return render_template("filter.html", names=app.config["FILTER_NAMES"])
    else:
        images = db.execute("SELECT image FROM imgs WHERE id = :id",
                            id=session["user_id"])
        imgs = []
        for i in range(len(images)):
            imgs.append(images[i]['image'])
        # print(imgs)
        #return render_template("filter.html", names=app.config["FILTER_NAMES"])
        return render_template("browse_images.html", images=imgs)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

if __name__ == '__main__':
    app.run()