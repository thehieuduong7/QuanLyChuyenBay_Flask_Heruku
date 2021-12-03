from flask import render_template, request, redirect, session, jsonify
from sqlalchemy.sql.sqltypes import Date
from __init__ import app, CART_KEY, my_login
from admin import*
from models import*
from flask_login import login_user
import utils
from datetime import datetime, date
import math

@my_login.user_loader
#Bỏ cả đối tượng vào biến current_user
def user_load(user_id):
    return NguoiDung.query.get(user_id)

@app.route("/")
def home():
    quy_dinh = utils.get_quydinh() 
    size = app.config["PAGE_SIZE"]
    index = request.args.get("page")
    if index:
        index = int(index)
    else:
        index = 1
    flights = utils.get_flight(noi_di=request.args.get("noidi"),
                                noi_den=request.args.get("noiden"),
                                time=request.args.get("time"))
    count = utils.count_flights(flights)
    flights = utils.paging(flights, index)
    
    newest_flight = utils.get_newest_flight()
    sanbay = utils.get_all_san_bay()

    return render_template("home.html", quy_dinh = quy_dinh,
                                        flights=flights,
                                        newest_flight = newest_flight,
                                        sanbay = sanbay,
                                        page_num=math.ceil(count/size),
                                        noi_di=request.args.get("noidi"),
                                        noi_den=request.args.get("noiden"),
                                        time = request.args.get("time"),
                                        index = index,
                                        mess = request.args.get("mess"))

@app.route("/login", methods=["POST"])
def login_execute():
    username = request.form.get('username')
    password = request.form.get('password')
    #password = str(hashlib.md5(pwd.encode("utf-8")).digest())

    user = NguoiDung.query.filter(NguoiDung.TenDN==username, NguoiDung.MatKhau==password).first()

    if user:
        if user.VaiTro == "A":
            login_user(user)
    return redirect("/admin")

@app.route("/login-user", methods = ["POST", "GET"])
def norlogin_user():
    if not current_user.is_authenticated:
        err_msg = ""
        if request.method == "POST":
            username = request.form.get("username")
            pwd = request.form.get("password")

            user = NguoiDung.query.filter(NguoiDung.TenDN == username, NguoiDung.MatKhau == pwd).first()

            if user:
                login_user(user)
                return redirect(request.args.get("next", "/"))
            else:
                err_msg = "Kiểm tra lại thông tin"

        return render_template("login-user.html", err_msg=err_msg)
    return redirect("/")
    
@app.route("/logout-user")
def normaluser_logout():
    logout_user()
    return redirect("/login-user")

@app.route("/register-user", methods=["POST", "GET"])
def register():
    err_msg = ""
    if request.method == 'POST':
        try:
            password = request.form.get("matkhau")    
            confirm_password = request.form.get("confirmmatkhau")
            if password.strip() == confirm_password.strip():
                data = request.form.copy()
                del data['confirmmatkhau']

                if utils.add_user(**data):
                    return redirect("/login-user")
                else:
                    err_msg = "Kiểm tra lại thông tin/Tên đăng nhập có thể đã tồn tại"
            else:
                err_msg = "Mật khẩu không khớp"
        except:
            err_msg = "Lỗi hệ thống/Vui lòng thử lại"

    return render_template("reg-user.html", err_msg = err_msg)

@app.route("/forgot-password")
def normaluer_forget_password():
    if not current_user.is_authenticated:
        return render_template("quen-mk.html")
    return redirect("/")

# Nhân Viên's
@app.route("/list-ve")
def list_ve():
    if current_user.VaiTro == "N":
        return render_template("list-ve.html")
@app.route("/ban-ve")
def ban_ve():
    if current_user.VaiTro == "N":
        return render_template("banve.html")
@app.route("/nhan-lich")
def nhan_lich():
    if current_user.VaiTro == "N":
        return render_template("nhanlichchuyenbay.html")
@app.route("/list-khach")
def list_khach():
    if current_user.VaiTro == "N":
        return render_template("list-khachhang.html")

# Khách hàng's
@app.route("/info-ve")
def info_ve():
    if current_user.VaiTro == "K":
        ve = utils.ve_da_mua(request.args.get("id"))
        return render_template("info-ve.html", ve=ve)
@app.route("/dat-ve-online")
def dat_ve_online():
    if current_user.VaiTro == "K":
        return render_template("dat-ve-online.html")

@app.route("/api/check-ve/<id_ve>", methods=['post'])
def check_ve(id_ve):
    ve = utils.get_ve(id_ve)
    if ve:
        if utils.check_ve(ve)==true:
            return jsonify({
                "error_code": 200
            })
    return jsonify({
        "error_code": 404
    })
    #if current_user.is_authenticated:
        #return render_template("doi-ve.html")
@app.route("/doi-ve")
def doi_tra_ve():
    return render_template("doi-ve.html")
# Khách hàng & Nhân viên
@app.route("/doi-ve", methods=['put'])
def doi_ve(id_ve, id_chuyen_bay, hang_ve):
    if utils.doi_ve(id_ve=id_ve, id_chuyen_bay=id_chuyen_bay, hang_ve=hang_ve)==true:
        pass
    #if current_user.is_authenticated:
        #return render_template("doi-ve.html")

@app.route("/api/tra-ve/<id_ve>", methods=['delete'])
def tra_ve(id_ve):
    #data = request.args.get('ve')
    #data = request.json
    #id_ve = str(data['id_ve'])
    if utils.xoa_ve(ve)==true:
        return jsonify({
            "error_code": 200,
        })
    return jsonify({
        "error_code": 400
    })
if __name__ == '__main__':
    app.run(debug=True)