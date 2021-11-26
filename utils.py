from math import prod
from datetime import datetime
from sqlalchemy import func
from models import*
from __init__ import app, db
from flask_login import current_user
import hashlib

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

def get_new_flight():
     return ChuyenBay.query.filter(ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).all()

def get_flight_by_id(fid):
    return ChuyenBay.query.get(fid)

def get_flight(noi_di=None, noi_den=None, time=None, page=None):
    flights = ChuyenBay.query
    if noi_di and noi_den and time:

        san_bay_di = SanBay.query.filter(SanBay.DiaChi==noi_di).first()
        san_bay_den = SanBay.query.filter(SanBay.DiaChi==noi_den).first()
        time = func.DATE(time)
        
        #date = ChuyenBay.ThoiGianXuatPhat.date()
        flights = flights.filter(ChuyenBay.sanbay_di==san_bay_di, 
                                        ChuyenBay.sanbay_den==san_bay_den,
                                        func.DATE(ChuyenBay.ThoiGianXuatPhat)==time).all()
    
    else:
        return ChuyenBay.query.all()
    
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