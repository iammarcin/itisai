import os
import socket

defaults = dict(
    environment = os.environ.get('NODE_ENV', None), # sherlock, production, local or None (for non docker env)
    openai_api_key = os.environ.get('OPENAI_API_KEY', None),
    groq_api_key = os.environ.get('GROQ_API_KEY', None),
    DEBUG = True,
    VERBOSE_SUPERB = False,
    AWS_REGION = "eu-west-1",
    AWS_S3_BUCKET = "myaiapps3bucket",
    MYSQL_HOST = "dbai.cvccw8kacdjk.eu-west-1.rds.amazonaws.com",
    MYSQL_DB = "aiapp",
    MYSQL_USER = "aitools",
    MYSQL_PASSWORD = os.environ.get('AWS_DB_PASS', None),
    ALLOWED_FILE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'mp3', 'mpeg', 'mpga', 'webm', 'wav', 'm4a', 'txt', 'mp4'],
)

if defaults['environment'] == 'production':
    defaults['LOCAL_MAIN_STORAGE']          = "/storage/testApi/"
elif defaults['environment'] == 'sherlock' :
    defaults['LOCAL_MAIN_STORAGE']          = "/storage/testApi/"
else: # local non docker
    home_dir                                = os.path.expanduser("~")
    #defaults['LOCAL_MAIN_STORAGE']          = f"{home_dir}/storage/testApi/"
    defaults['LOCAL_MAIN_STORAGE']          = "/storage/testApi/"
