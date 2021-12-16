import time
import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError

from flask import Flask, render_template, jsonify, flash, request, redirect, url_for, send_from_directory
import werkzeug
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

AWS_ACCESS_KEY = 'ASIAXMEHLIGH6VUX4N6C'
AWS_SECRET_ACCESS_KEY = 'ZtS2v86qLAwIvX2b3HLXZAcv/D3MQSy7D86rmaQI'
AWS_DOMAIN= "http://inputdancc.s3.amazonaws.com/"
AWS_BUCKET_NAME= "inputdancc"

def upload_file_to_s3(file, acl="public-read"):
    s3 = boto3.client(
    "s3",
        aws_access_key_id="ASIAXMEHLIGH6VUX4N6C",
        aws_secret_access_key="ZtS2v86qLAwIvX2b3HLXZAcv/D3MQSy7D86rmaQI"
    )
    filename = secure_filename(file.filename)
    try:
        s3.upload_fileobj(
            file,
            "inputdancc",
            filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        error = str(e)
        return False, error
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return True, file.filename

@app.errorhandler(404)
def notfound(e):
    return render_template("404/404_error.html"), 404

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #result, output = upload_file_to_s3(file) 
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # if result:
            #     # flash("Success upload")
            #     # return redirect("/uploads/"+output)
            #     return output
            # else:
            #     #flash("Unable to upload, try again")
            #     # return redirect("/")
            #     return output
            return redirect('/uploads/'+filename)
    return render_template('index.html')

@app.route('/uploads/<name>')
def download_file(name):
    partitioned_string = name.rpartition('.')
    file_path = "./uploads/" + name
    audio_name = partitioned_string[0] +".mp3"
    output_path = "./uploads/" +audio_name

    os.system("ffmpeg -i {} {}".format(file_path, output_path))

    #uploaded = upload_to_aws(file_path, 'inputdancc', name)

    return send_from_directory(app.config["UPLOAD_FOLDER"], audio_name)

# @app.route('/')
# def index():
#     return render_template('index.html')