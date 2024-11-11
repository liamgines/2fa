py -m venv venv
CALL venv\Scripts\activate.bat

:: The following installs: selenium, flask, flask-wtf and python-dotenv
pip install -r requirements.txt
exit()