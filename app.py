import os
import subprocess
from datetime import datetime
import warnings

import pytz
from dotenv import dotenv_values
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

credentials_file = "credentials.json"

def start_backup_process():
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    folder_id = "12U9HviHK7u3EVMZCktK3RVnSAewGim8b"
    project_path = "/home/lorxe.site/public_html"

    # read variables from .env file
    env_vars = dotenv_values(f'{project_path}/.env')
    app_name = env_vars.get("APP_NAME")
    db_database = env_vars.get("DB_DATABASE")

    # create file name
    timezone = pytz.timezone('Asia/Yangon')
    current_time = datetime.now(timezone)
    file_name = f'{app_name}_' + current_time.strftime("%d_%m_%Y_%I_%M_%p") + '.sql.gz'
    
    command = f'mysqldump --user=root "{db_database}" | gzip > "{file_name}"'

    try:
        subprocess.run(command, shell=True, check=True)
        
        try:
            # upload to Drive
            file = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
            file['mimeType'] = 'application/gzip'
            file.SetContentFile(file_name)
            file.Upload()
        except Exception as e:
            os.remove(credentials_file)
        
        # delete file
        os.remove(file_name)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        
if os.path.exists(credentials_file):
    start_backup_process()
else:
    warnings.filterwarnings("ignore", category=UserWarning)
    GoogleAuth().CommandLineAuth()
