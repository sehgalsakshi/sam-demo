import bcrypt
from datetime import datetime, date
user_schema = {
    'image_id': {'field_type':str, 'max_len':200},
    'date_created': {'auto_now_add':True},
    'is_recurring': {'field_type':bool, 'default':False},
    'email_verified_at': {'field_type':str, 'max_len':200},
    'first_name': {'field_type':str, 'max_len':200},
    'last_name': {'field_type':str, 'max_len':200},
    'fullname': {'field_type':str, 'max_len':200},
    'phone_number': {'field_type':str, 'max_len':14},
    'profile_type': {'field_type':str, 'max_len':200},
    'balance': {'field_type':str, 'max_len':200},
    'tenant_id': {'field_type':str, 'max_len':200},
    'promo_code': {'field_type':str, 'max_len':200},
    'formatted_date': {'field_type':str, 'max_len':200},
    'account_number': {'field_type':str, 'max_len':10},
    'father_name': {'field_type':str, 'max_len':200},
    'status': {'field_type':str, 'max_len':200},
    'address': {'field_type':str, 'max_len':200},
    'dob': {'field_type':str, 'max_len':200},
    'city': {'field_type':str, 'max_len':200},
    'gender': {'field_type':str, 'max_len':200},
    'rating': {'field_type':str, 'max_len':200},
    'state': {'field_type':str, 'max_len':200},
    'country': {'field_type':str, 'max_len':200},
    'delete_flag': {'field_type':bool, 'default':False},
    'last_logged_in': {'auto_now':True},
    'last_modified': {'auto_now':True},
    'bvn': {'field_type':str, 'max_len':14},
    'pin': {'field_type':str, 'max_len':14},
    'question_1': {'field_type':str, 'max_len':200},
    'question_2': {'field_type':str, 'max_len':200},
    'question_3': {'field_type':str, 'max_len':200},
    'answer_1': {'field_type':str, 'max_len':200},
    'answer_2': {'field_type':str, 'max_len':200},
    'answer_3': {'field_type':str, 'max_len':200},
    'docType': {'field_type':str, 'max_len':200},
    'last_login': {'auto_now_add':True},
    'date_joined': {'field_type':date, 'null':True},
    'is_superuser': {'field_type':bool, 'default':False},
    'is_staff': {'field_type':bool, 'default':False},
    'is_active': {'field_type':bool, 'default':False},
    'username': {'field_type':str, 'max_len':200, 'unique':True},
    'countryCode': {'field_type':str, 'max_len':200},
    'receive_notifications': {'field_type':bool, 'default':False},
    'date_of_birth': {'field_type':str, 'max_len':200},
}

def get_user_data(data, is_create=True):
    user_data = {}
    
    for k,v in data.items():
        if k== 'password':
            user_data['password_salt'] = get_hashed_password(data['password'])
        if k not in user_schema.keys():
            return False, 'Contains extra fields'
        else:
            val = add_validate_user_data(k, v, is_create)
            if val[0] == False:
                return False, val[1]
            else:
                user_data[k] = True, val[1]
    
    for k in list(user_schema.keys() - data.keys()):
        val = add_validate_user_data(k, False, is_create)
        if val[0] == False:
            return False, val[1]
        else:
            user_data[k] = True, val[1]
        

def add_validate_user_data(k, v, is_create):
    validation_data = user_schema[k]
    is_auto_now = validation_data.get('auto_now', False)
    is_auto_now_add = validation_data('auto_now_add', False)
    if is_auto_now or (is_auto_now_add and is_create):
        return True, str(datetime.timestamp(datetime.now()))
    default = validation_data.get('default','')
    is_null = validation_data.get('null','')
    if not v and not is_null:
        return False, k + ' is a required field'
    elif is_null:
        return True, default
    is_type_correct = isinstance(v, validation_data['field_type'])
    if not is_type_correct:
        return False, k + ' type must be '+ str(validation_data['field_type'])
    max_len = validation_data('max_len', False)
    if max_len and len(v)> max_len:
        return False, k + ' exceeds max length'
    return True, v

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)

