import bcrypt
import jwt
import datetime
import os

################
# this is just test implementation
################


# Replace this with your actual secret key
JWT_SECRET_KEY = os.environ.get('MY_AUTH_TOKEN', None)
# Simulate a database result with a test user's information
# Replace with actual query result in a real scenario
db_result = {
    'id': 1,
    'accountName': 'myUser',
    'email': 'mn@gmail.com',
    'password': bcrypt.hashpw('testpassword'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
    'lang': 'en'
}

def generate_token(user_id, account_name, expires_in):
    payload = {
        'id': user_id,
        'email': account_name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def login_user(email, password):
    # Simulate a database query
    if email != db_result['email']:
        return {'code': 401, 'success': False, 'message': 'Unauthorized'}

    hashed_password = db_result['password']

    # Check if the provided password matches the stored hashed password
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return {'code': 401, 'success': False, 'message': 'Unauthorized'}

    # Determine token expiration
    # for normal user
    expires_value = 15 * 86400  # 15 days in seconds
    # for admin user
    if db_result['id'] == 1:
        expires_value = 31536000  # 1 year in seconds

    # Generate the JWT token
    token = generate_token(db_result['id'], db_result['accountName'], expires_value)
    return {
        'code': 200,
        'success': True,
        'message': {
            'status': 'Authorized',
            'userId': db_result['id'],
            'accessToken': token
        }
    }

# Test the login function
test_email = 'mn@gmail.com'
test_password = 'testpassword'

response = login_user(test_email, test_password)
print(response)
