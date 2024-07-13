import os
import socket

defaults = dict(
    # sherlock, production, local or None (for non docker env)
    environment=os.environ.get('NODE_ENV', None),
    openai_api_key=os.environ.get('OPENAI_API_KEY', None),
    groq_api_key=os.environ.get('GROQ_API_KEY', None),
    DEBUG=True,
    VERBOSE_SUPERB=False,
    MYSQL_USER="aitools",
    MYSQL_PASSWORD=os.environ.get('AWS_DB_PASS', None),
    ALLOWED_FILE_TYPES=['jpg', 'jpeg', 'png', 'gif', 'mp3',
                        'mpeg', 'mpga', 'webm', 'wav', 'm4a', 'txt', 'mp4', 'opus', 'pdf'],
    # error message - in config - because it is used in multiple places (for sending error, but also for NOT storing data in DB)
    # if we change here - in restore function in android - it's also set (in ChatHelper)
    ERROR_MESSAGE_FOR_TEXT_GEN="Error in Text Generator. Try again!",
    JWT_SECRET_KEY=os.environ.get('MY_AUTH_TOKEN', None),
)

if defaults['environment'] == 'production':
    defaults['LOCAL_MAIN_STORAGE'] = "/storage/testApi/"
    defaults['AWS_REGION'] = "eu-south-2"
    defaults['AWS_S3_BUCKET'] = "myaiappess3bucket"
    defaults['MYSQL_HOST'] = "db.goodtogreat.life"
    defaults['MYSQL_DB'] = "aiapp"
elif defaults['environment'] == 'sherlock':
    defaults['LOCAL_MAIN_STORAGE'] = "/storage/testApi/"
    defaults['AWS_REGION'] = "eu-south-2"
    defaults['AWS_S3_BUCKET'] = "myaiappess3bucketnonprod"
    defaults['MYSQL_HOST'] = "db.goodtogreat.life"
    defaults['MYSQL_DB'] = "aiapp_nonprod"
    # defaults['MYSQL_DB'] = "aiapp"
else:  # local non docker
    home_dir = os.path.expanduser("~")
    # defaults['LOCAL_MAIN_STORAGE']          = f"{home_dir}/storage/testApi/"
    defaults['LOCAL_MAIN_STORAGE'] = "/storage/testApi/"
    defaults['AWS_REGION'] = "eu-south-2"
    defaults['AWS_S3_BUCKET'] = "myaiappess3bucketnonprod"
    defaults['MYSQL_HOST'] = "db.goodtogreat.life"
    defaults['MYSQL_DB'] = "aiapp_nonprod"
