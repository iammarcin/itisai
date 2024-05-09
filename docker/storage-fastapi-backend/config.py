import os
import socket

# get the hostname
defaults = dict(
    environment = os.environ.get('NODE_ENV', None), # sherlock, production, local or None (for non docker env)
    openai_api_key = os.environ.get('OPENAI_API_KEY', None),
    groq_api_key = os.environ.get('GROQ_API_KEY', None),
    DEBUG = True,
    VERBOSE_SUPERB = False,
)

if defaults['environment'] == 'production':
    defaults['LOCAL_MAIN_STORAGE']          = "/storage/testApi/"
elif defaults['environment'] == 'sherlock' :
    defaults['LOCAL_MAIN_STORAGE']          = "/storage/testApi/"
else: # local non docker
    home_dir                                = os.path.expanduser("~")
    #defaults['LOCAL_MAIN_STORAGE']          = f"{home_dir}/storage/testApi/"
    defaults['LOCAL_MAIN_STORAGE']          = "/storage/testApi/"
