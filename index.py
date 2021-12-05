from flask import render_template, request, redirect, session, jsonify
from sqlalchemy.sql.sqltypes import Date
from ControllerBangGiaVe import BangGiaVeController
from __init__ import app, CART_KEY, my_login
from admin import*
from models import*
from flask_login import login_user
import utils
from datetime import datetime, date
import math
from ControllerTicket import TicketController
from ControllerQuyDinh import QuyDinhController
from ControllerNhapLich import NhapLichController
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
    
    ListBangGiaVe = BangGiaVeController().listBangGiaVe()

    return render_template("home.html", quy_dinh = quy_dinh,
                                        flights=flights,
                                        newest_flight = newest_flight,
                                        sanbay = sanbay,
                                        page_num=math.ceil(count/size),
                                        noi_di=request.args.get("noidi"),
                                        noi_den=request.args.get("noiden"),
                                        time = request.args.get("time"),
                                        index = index,ListBangGiaVe=ListBangGiaVe)

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
@app.route("/ban-ve/<id_cb>/<hang>/<int:soluong>",methods=['Post','Get'])
def ban_ve(id_cb,hang,soluong):
    if current_user.VaiTro == "N":
        soluong=int(soluong)
        id_cb=int(id_cb)
        cb= ChuyenBay.query.get(id_cb)
        if(request.method=='GET'):
            if(not cb): return 'không tìm thấy chuyến bay'
            return render_template("banve.html",
                    number_kh=soluong,chuyenBay=cb,hangVe=hang)
        else:
            list_kh=[]
            veDAO = TicketController()
            for i in range(1,int(soluong)+1):
                data_kh={}
                data_kh['HoTenKH']=request.form.get('HoTenKH'+str(i))
                data_kh['GioiTinh']=request.form.get('GioiTinh'+str(i))
                data_kh['NamSinh']=request.form.get('NamSinh'+str(i))
                data_kh['SDT']=request.form.get('SDT'+str(i))
                data_kh['CMND']=request.form.get('CMND'+str(i))
                data_kh['Email']=request.form.get('Email'+str(i))
                data_kh['HinhAnh'] = request.files['HinhAnh'+str(i)]
                list_kh.append(data_kh.copy())
            
            mess="success"  
            contentMess="Bán vé thành công!!! vui lòng kiểm tra gmail!!!"
            
            result= veDAO.BanVeNhieuVe(id_cb,hang,list_kh)
            if(result!=True):
                mess="error"
                contentMess=result
            cb= ChuyenBay.query.get(id_cb)
            return render_template("banve.html",
                    number_kh=soluong,chuyenBay=cb,hangVe=hang,mess=mess,contentMess=contentMess)

    return 'faile'


@app.route("/nhan-lich")
def nhan_lich():
    if current_user.VaiTro == "N":
        listAllMB = MayBay.query.all()
        listAllSB=SanBay.query.all()
        quyDinhDAO = QuyDinhController()
        minBay= quyDinhDAO.ThoiGianBayToiThieu().NoiDung
        soTG = quyDinhDAO.SoSanBayTrungGianToiDa().NoiDung
        minDung=quyDinhDAO.ThoiGianDungToiThieu().NoiDung
        maxDung=quyDinhDAO.ThoiGianDungToiDa().NoiDung
        return render_template("nhanlichchuyenbay.html",listAllMB=listAllMB,
                               listAllSB=listAllSB,
                        minBay=minBay,soTG=soTG,minDung=minDung,maxDung=maxDung)
        
def checkInputDataNhanLich(data):
    Id_MayBay=data['Id_MayBay']
    Id_SanBay_Di=data['Id_SanBay_Di']
    Id_SanBay_Den=data['Id_SanBay_Den']
    ThoiGianXuatPhat=data['ThoiGianXuatPhat']
    ThoiGianBay=data['ThoiGianBay']
    SoLuongChoNgoi=data['SoLuongChoNgoi']
    if(Id_SanBay_Den==Id_SanBay_Di): return "Trùng sân bay"

    ListTrungGian = data['ListTrungGian']
    for trungGian in ListTrungGian:
        if(trungGian["Id_SanBay"]==Id_SanBay_Di or
           trungGian["Id_SanBay"]==Id_SanBay_Den): return "Trùng sân bay"
        
        
    ListHangVe = data['ListHangVe']
    sumSoVe=0
    for hangVe in ListHangVe:
        sumSoVe+= int(hangVe['SoGhe'])
    if(sumSoVe>SoLuongChoNgoi):
        return "Số lượng vé nhiều hơn số chỗ ngồi"
    return 'success'
    
@app.route("/nhan-lich-post",methods=['Post'])
def nhan_lich_post():
    if current_user.VaiTro == "N":
        data={}
        Id_MayBay = request.form.get('Id_MayBay')
        Id_SanBay_Di = int(request.form.get('Id_SanBay_Di'))
        Id_SanBay_Den= int(request.form.get('Id_SanBay_Den'))
        ThoiGianXuatPhat= request.form.get('ThoiGianXuatPhat')
        ThoiGianBay= int(request.form.get('ThoiGianBay'))
        SoLuongChoNgoi= int(request.form.get('SoLuongChoNgoi'))
        listId_SanBayTG = request.form.getlist('TrungGian-select')
        listthoiGianDung=request.form.getlist('thoiGianDung')
        listChuThich=request.form.getlist('ChuThich-text')
        listhangVe= request.form.getlist('hangVe-text')
        listgiaVe= request.form.getlist('giaVe-text')
        listsoShe= request.form.getlist('soGhe-text')
        data['Id_MayBay']=Id_MayBay
        data['Id_SanBay_Di']=Id_SanBay_Di
        data['Id_SanBay_Den']=Id_SanBay_Den
        data['ThoiGianXuatPhat']=ThoiGianXuatPhat
        data['ThoiGianBay']=ThoiGianBay
        data['SoLuongChoNgoi']=SoLuongChoNgoi
        data['ListTrungGian']=[]
        data['ListHangVe']=[]
  
        for i in range(len(listId_SanBayTG)):
            trungGian ={}
            trungGian['Id_SanBay']=int(listId_SanBayTG[i])
            trungGian['ThoiGianDung']=int(listthoiGianDung[i])
            trungGian['GhiChu']=listChuThich[i]
            data['ListTrungGian'].append(trungGian.copy())
        for i in range(len(listhangVe)):
            bangGia ={}
            bangGia['HangVe']=listhangVe[i]
            bangGia['GiaVe']=float(listgiaVe[i])
            bangGia['SoGhe']=int(listsoShe[i])
            data['ListHangVe'].append(bangGia.copy())
        
        listAllMB = MayBay.query.all()
        listAllSB=SanBay.query.all()
        mess='success'
        contentMess='Nhập chuyến bay thành công!!!'
        
        if(checkInputDataNhanLich(data)!='success'):
            mess='error'
            contentMess=checkInputDataNhanLich(data)
            return render_template("nhanlichchuyenbay.html",listAllMB=listAllMB,
                               listAllSB=listAllSB,mess=mess,
                               contentMess=contentMess)
            
        nhapLichDAO = NhapLichController()
        result = nhapLichDAO.nhapLich(data)
        if(result!=True):
            mess='error'
            contentMess=result
            
        quyDinhDAO = QuyDinhController()
        minBay= quyDinhDAO.ThoiGianBayToiThieu().NoiDung
        soTG = quyDinhDAO.SoSanBayTrungGianToiDa().NoiDung
        minDung=quyDinhDAO.ThoiGianDungToiThieu().NoiDung
        maxDung=quyDinhDAO.ThoiGianDungToiDa().NoiDung

        return render_template("nhanlichchuyenbay.html",listAllMB=listAllMB,
                               listAllSB=listAllSB,mess=mess,
                               contentMess=contentMess,minBay=minBay,
                               soTG=soTG,minDung=minDung,maxDung=maxDung)
        
@app.route("/list-khach")
def list_khach():
    if current_user.VaiTro == "N":
        return render_template("list-khachhang.html")

# Khách hàng's
@app.route("/info-ve")
def info_ve():
    if current_user.VaiTro == "K":
        return render_template("info-ve.html")
@app.route("/dat-ve-online/<int:id_cb>/<hang>/<int:soluong>",methods=['Get','Post'])
def dat_ve_online(id_cb,hang,soluong):
    if current_user.is_authenticated:
        soluong=int(soluong)
        id_cb=int(id_cb)
        cb= ChuyenBay.query.get(id_cb)
        minDat = int(QuyDinhController().ThoiGianDatVeToiThieu().NoiDung)
        if(request.method=='GET'):
            if(not cb): return 'không tìm thấy chuyến bay'
            return render_template("dat-ve-online.html",
                number_kh=soluong,chuyenBay=cb,hangVe=hang,minDat=minDat)
        else:
            list_kh=[]
            veDAO = TicketController()
            for i in range(1,int(soluong)+1):
                data_kh={}
                data_kh['HoTenKH']=request.form.get('HoTenKH'+str(i))
                data_kh['GioiTinh']=request.form.get('GioiTinh'+str(i))
                data_kh['NamSinh']=request.form.get('NamSinh'+str(i))
                data_kh['SDT']=request.form.get('SDT'+str(i))
                data_kh['CMND']=request.form.get('CMND'+str(i))
                data_kh['Email']=request.form.get('Email'+str(i))
                data_kh['HinhAnh'] = request.files['HinhAnh'+str(i)]
                list_kh.append(data_kh.copy())
            
            mess="success"  
            contentMess="Bán vé thành công!!! vui lòng kiểm tra gmail!!!"
            
            result= veDAO.DatVeNhieuVe(id_cb,hang,list_kh)
            if(result!=True):
                mess="error"
                contentMess=result
            cb= ChuyenBay.query.get(id_cb)
            return render_template("dat-ve-online.html",
                    number_kh=soluong,chuyenBay=cb,hangVe=hang,mess=mess,contentMess=contentMess,
                    minDat=minDat)
    return 'faile',403   

# Khách hàng & Nhân viên
@app.route("/doi-ve")
def doi_ve():
    if current_user.is_authenticated:
        return render_template("doi-ve.html")
if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)