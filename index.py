from flask import render_template, request, redirect, session, jsonify
from __init__ import app, CART_KEY, my_login
from admin import*
from models import NguoiDung
from flask_login import login_user

@my_login.user_loader
#Bỏ cả đối tượng vào biến current_user
def user_load(user_id):
    return NguoiDung.query.get(user_id)

@app.route("/login", methods=["POST"])
def login_execute():
    username = request.form.get('username')
    password = request.form.get('password')
    #password = str(hashlib.md5(pwd.encode("utf-8")).digest())

    user = NguoiDung.query.filter(NguoiDung.TenDN==username, NguoiDung.MatKhau==password).first()

    if user:
        login_user(user)
    return redirect("/admin")

if __name__ == '__main__':
    app.run(debug=True)