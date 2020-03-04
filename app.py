import os, requests
from flask import Flask, request, send_from_directory

# file
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)
app.config.from_object(__name__)

UPLOAD_FOLDER = './storage/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello_world():
    return 'Hello, World!'

# -----------------------------------------------------------------------------------------------------
# -------------------------------------- Authentication -----------------------------------------------
# -----------------------------------------------------------------------------------------------------

def auth(header):
    if requests.request("GET", 'http://oauth.infralabs.cs.ui.ac.id/oauth/resource', headers={"Authorization":header}).status_code == 200:
        return True
    else:
        return False

# -----------------------------------------------------------------------------------------------------
# ---------------------------------------- Upload File ------------------------------------------------
# -----------------------------------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['POST'])
def upload():
    if auth(request.headers.get('Authorization')):
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return {"message":"No file part"}
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return {"message":"No selected file"}
            if file and allowed_file(file.filename):
                filename_w_frmt = secure_filename(file.filename)
                filename = filename_w_frmt.replace(" ", "_")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                pos_dot = max([pos for pos, char in enumerate(filename) if char == "."])
                filename = filename[:pos_dot]

                zf = zipfile.ZipFile(app.config['UPLOAD_FOLDER'] + filename + ".zip", mode='w')
                zf.write(app.config['UPLOAD_FOLDER'] + filename_w_frmt)
                zf.close()
                return {"message":"Success!", "link":"/download/"+ filename+".zip"}

@app.route('/download/<filename>')
def uploaded_file(filename):
    if auth(request.headers.get('Authorization')):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)