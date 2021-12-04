from functools import wraps
from flask import request, render_template, redirect, session

# 許可されているファイルの拡張子のセット
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    