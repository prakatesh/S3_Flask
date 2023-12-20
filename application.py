from flask import Flask,render_template,request,send_file,make_response
import boto3
from botocore.exceptions import ClientError
import logging
import os
s3_client = boto3.client('s3')
s3 = boto3.client('s3', aws_access_key_id='AKIASC3ASZET4RA6WVU5', aws_secret_access_key='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')
S3_BUCKET = 'test1-show-in-web'

application=Flask(__name__)

@application.route('/',methods=['POST','GET'])
def index():
    try:
        objects = s3.list_objects(Bucket=S3_BUCKET)['Contents']
        return render_template('index.html',objects=objects)
    except Exception as e:
        return f"Error: {str(e)}"


@application.route('/upload',methods=['POST','GET'])
def upload_file():
    file=request.files['file']
    if file.filename=="":
        return 'No file is selected'

    try:
        if request.form['saveas']=="":
            filename=file.filename
        else:
            filename=request.form['saveas']+os.path.splitext(file.filename)[1]
        
        s3.upload_fileobj(file, S3_BUCKET, filename)
        return index()

    except ClientError as e:
        logging.error(e)
    
@application.route('/view_object/<key>',methods=['POST','GET'])
def view_object(key):
    try:
        response=s3.get_object(Bucket=S3_BUCKET,Key=key)
        content_type=response.get('ContentType','application/octet-stream')

        return send_file(response['Body'],mimetype=content_type,as_attachment=True,download_name=key)
    
    except Exception as e:
        return f"Error: {str(e)}"

@application.route('/rename',methods=['POST','GET'])
def rename():
    file_name, file_extension = os.path.splitext(request.form['old_name'])
    s3.copy_object(
        Bucket=S3_BUCKET,CopySource={'Bucket': S3_BUCKET, 'Key': request.form['old_name']},Key=request.form['new_name']+file_extension
    )
    s3.delete_object(
        Bucket=S3_BUCKET,
        Key=request.form['old_name']
    )
    return index()

@application.route('/delete/<key>',methods=['POST',"GET"])
def delete(key):
    s3.delete_object(Bucket=S3_BUCKET,Key=key)
    return index()

if __name__=="__main__":
    application.run(debug=True)