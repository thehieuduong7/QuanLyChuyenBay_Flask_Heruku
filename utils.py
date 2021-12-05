from math import prod
from datetime import datetime, timedelta, date
from sqlalchemy import func
from sqlalchemy.sql.expression import null
from flask_mail import Message
from models import*
from __init__ import app, db, mail
from flask_login import current_user
import hashlib
from sqlalchemy import exc

def add_user(tendangnhap, tennguoidung, matkhau): 
    get_user = NguoiDung.query.filter(NguoiDung.TenDN == tendangnhap).all()
    if not get_user:
        user = NguoiDung(TenDN = tendangnhap, 
                    MatKhau = matkhau, 
                    VaiTro = "K",
                    TenNguoiDung = tennguoidung)
        db.session.add(user)
        try:
            db.session.commit()
            return True      
        except:
            return False
    else:
        return False



def get_quydinh():
    return QuyDinh.query.all()

def count_flight_by_san_bay(san_bay_di):
    return ChuyenBay.query.filter(ChuyenBay.Id_SanBay_Di==san_bay_di, ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).count()

def get_flight_by_san_bay(san_bay=None):
    return ChuyenBay.query.filter(ChuyenBay.sanbay_di==san_bay, ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).order_by(ChuyenBay.ThoiGianXuatPhat).all()

def get_new_flight():
     return ChuyenBay.query.filter(ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).all()

def get_flight_by_id(fid):
    return ChuyenBay.query.get(fid)

def get_flight(noi_di=None, noi_den=None, time=None):
    flights = ChuyenBay.query
    if noi_di and noi_den and time:
        try:
            san_bay_di = SanBay.query.filter(SanBay.DiaChi==noi_di).first()
            san_bay_den = SanBay.query.filter(SanBay.DiaChi==noi_den).first()
            time = func.DATE(time)
            
            #date = ChuyenBay.ThoiGianXuatPhat.date()
            flights = flights.filter(ChuyenBay.sanbay_di==san_bay_di, 
                                            ChuyenBay.sanbay_den==san_bay_den,
                                            func.DATE(ChuyenBay.ThoiGianXuatPhat)==time).all()
        except Exception:
            return get_new_flight()
    else:
        return get_new_flight()
    
    return flights

def paging(flights, page):
    if flights:
        size = app.config["PAGE_SIZE"]
        start = (page-1)*size
        end = start+size
        return flights[start:end]
    return flights

def count_flights(flights):
    return len(flights)

def count_ve(ve):
    return len(ve)

def get_newest_flight():
    return ChuyenBay.query.filter(ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).order_by(ChuyenBay.ThoiGianXuatPhat).limit(1)

def get_all_san_bay():
    return SanBay.query.all()

def get_san_bay_by_id(id):
    return SanBay.query.get(id)



def get_ve(ve):
    ma = ve.split('-')
    try:
        kh = KhachHang.query.filter(KhachHang.SDT==ma[1]).first()
        if kh:
            return Ve.query.filter(Ve.id==ma[0], Ve.khachhang==kh,
                                    Ve.Id_KhachHang==ma[2]).first()
        return
    except:
        return

def check_ve(ve):
    quy_dinh = QuyDinh.query.filter(QuyDinh.QuyDinh=="TGDatVeTreNhat").first()
    if quy_dinh:
        day = int(quy_dinh.NoiDung)
        time = ChuyenBay.query.filter(ChuyenBay.id==ve.Id_ChuyenBay, ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now()+timedelta(days=+day))).first()
    else:
        time = ChuyenBay.query.filter(ChuyenBay.id==ve.Id_ChuyenBay, ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now()+timedelta(days=+1))).first()
    if time:
        return true
    return false

def check_ve_moi(id_chuyen_bay, hang_ve):
    so_ghe = BangGiaVe.query.filter(BangGiaVe.Id_ChuyenBay==id_chuyen_bay,
                                    BangGiaVe.HangVe==hang_ve).first()
    so_ghe_het = Ve.query.filter(Ve.Id_ChuyenBay==id_chuyen_bay,
                                 Ve.HangVe==hang_ve).count()
    if so_ghe.SoGhe>so_ghe_het:
        return true
    return false

def xoa_ve(ve):
    try:     
        gia = BangGiaVe.query.filter(BangGiaVe.Id_ChuyenBay==ve.Id_ChuyenBay,
                                     BangGiaVe.HangVe==ve.HangVe).first()
        doanhthu = DoanhThuThang.query.filter(DoanhThuThang.Id_ChuyenBay==ve.Id_ChuyenBay).first()
        
        if doanhthu:
            doanhthu.DoanhThu -= gia.GiaVe
            doanhthu.SoVeBanDuoc -= 1
            gia.SoGhe += 1
            db.session.add(gia)
            db.session.add(doanhthu)   
            db.session.commit()     
            db.session.delete(ve)       
            db.session.commit()
            return true
        return false
    except exc.SQLAlchemyError:
        db.session.rollback()
        return false

def doi_ve(ve, id_chuyen_bay, hang_ve):
    try:   
        gia_truoc = BangGiaVe.query.filter(BangGiaVe.Id_ChuyenBay==ve.Id_ChuyenBay,
                                     BangGiaVe.HangVe==ve.HangVe).first()
        gia_sau = BangGiaVe.query.filter(BangGiaVe.Id_ChuyenBay==id_chuyen_bay,
                                     BangGiaVe.HangVe==hang_ve).first()
        doanh_thu_truoc = DoanhThuThang.query.filter(DoanhThuThang.Id_ChuyenBay==ve.Id_ChuyenBay).first()
        doanh_thu_sau = DoanhThuThang.query.filter(DoanhThuThang.Id_ChuyenBay==id_chuyen_bay).first()
        if doanh_thu_truoc and doanh_thu_sau:
            doanh_thu_truoc.DoanhThu -= gia_truoc.GiaVe
            doanh_thu_truoc.SoVeBanDuoc -= 1
            doanh_thu_sau.DoanhThu += gia_sau.GiaVe
            doanh_thu_sau.SoVeBanDuoc += 1
            db.session.add(doanh_thu_truoc)
            db.session.add(doanh_thu_sau)  
            db.session.commit()          
        ve.Id_ChuyenBay = id_chuyen_bay
        ve.HangVe = hang_ve
        db.session.add(ve) 
        db.session.flush()
        db.session.refresh(ve)
        # db.session.commit()
        # return true
        if send_mail(ve)==true:      
            db.session.commit()
            return true
        return false
    except exc.SQLAlchemyError:
        db.session.rollback()
        return false

def send_mail(veMayBay):
    if veMayBay:
        name = veMayBay.khachhang.HoTenKH
        id_ve=str(veMayBay.id) + '-' + str(veMayBay.khachhang.SDT) + '-' + str(veMayBay.Id_KhachHang)
        thoiGianDat= veMayBay.ThoiGianDatVe
        hangVe=veMayBay.HangVe
                
        chuyenBay = veMayBay.chuyenbay
        id_chuyenBay=chuyenBay.id
        sanBayDi=chuyenBay.sanbay_di.DiaChi+' ('+chuyenBay.sanbay_di.TenSB+')'
        sanBayDen=chuyenBay.sanbay_den.DiaChi+' ('+chuyenBay.sanbay_den.TenSB+')'
        bangGiaVe = BangGiaVe.query.filter_by(Id_ChuyenBay=id_chuyenBay,HangVe=hangVe ).first()
        giaVe=bangGiaVe.GiaVe
                
        email = veMayBay.khachhang.Email
        content = '''
                    Hang hang khong gia re                                      Sai gon {time}
                                                            THONG TIN VE MAY BAY
                    Khach hang: {name}
                    Ma ve: {id_ve}
                    Chuyen bay: {id_chuyenBay}
                    San bay di: {sanBayDi:15} San bay den:{sanBayDen:20}
                    Hang ve: {hangVe}
                    Gia ve: {giaVe} dong
                    Thoi gian dat: {thoiGianDat}
                '''
        contentSend = content.format(time=date.today(),name=name,id_ve=id_ve,
                    id_chuyenBay=id_chuyenBay,sanBayDi=sanBayDi,sanBayDen=sanBayDen,hangVe=hangVe,
                    giaVe=giaVe,thoiGianDat=thoiGianDat)
        ms={}
        ms['email']=email
        ms['contentSend']=contentSend
        msg = Message(subject="Ve may bay gia re",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[ms['email']],
                body=ms['contentSend'])
        mail.send(msg)
        return true
    return false

def ve_da_mua(id):
     return Ve.query.filter(Ve.khachhang.has(KhachHang.id_nguoidung==id)).order_by(Ve.ThoiGianDatVe.desc()).all()
    # kh = KhachHang.query.filter(KhachHang.id_nguoidung==id)
    # if kh:         
    #     return Ve.query.filter(Ve.khachhang==kh).first()
    # else:
    #     return

def get_all_ve():
    return Ve.query.join(ChuyenBay, Ve.Id_ChuyenBay==ChuyenBay.id).filter(ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).order_by(Ve.ThoiGianDatVe.desc()).all()

def paging_ve(ve, page):
    if ve:
        size = app.config["PAGE_SIZE"]
        start = (page-1)*size
        end = start+size
        return ve[start:end]
    return ve

if __name__== '__main__':
    with app.app_context():
        ve = Ve.query.get(19)
        print(send_mail(ve))