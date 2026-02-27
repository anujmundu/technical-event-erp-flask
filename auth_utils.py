from functools import wraps
from flask import session, redirect, url_for, render_template

# login required
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# role check
def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") != role_name:
                # show styled message page
                return render_template("message.html", message="Unauthorized Access", back_url=url_for('login')), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator