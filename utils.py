from math import prod
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.sql.expression import null
from models import*
from __init__ import app, db
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

def get_flight(noi_di=None, noi_den=None, time=None, page=None, san_bay=None):
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
    time = ChuyenBay.query.filter(ChuyenBay.id==ve.Id_ChuyenBay, ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now()+timedelta(days=+1))).first()
    if time:
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
            gia_truoc.SoGhe += 1
            gia_sau.SoGhe -= 1
            db.session.add(doanh_thu_truoc)
            db.session.add(doanh_thu_sau)  
            db.session.add(gia_truoc)
            db.session.add(gia_sau)
            db.session.commit()          
        ve.Id_ChuyenBay = id_chuyen_bay
        ve.HangVe = hang_ve
        db.session.add(ve)       
        db.session.commit()
        return true
    except exc.SQLAlchemyError:
        db.session.rollback()
        return false


def ve_da_mua(id):
     return Ve.query.filter(Ve.khachhang.has(KhachHang.id_nguoidung==id)).order_by(Ve.ThoiGianDatVe.desc()).all()
    # kh = KhachHang.query.filter(KhachHang.id_nguoidung==id)
    # if kh:         
    #     return Ve.query.filter(Ve.khachhang==kh).first()
    # else:
    #     return
    
