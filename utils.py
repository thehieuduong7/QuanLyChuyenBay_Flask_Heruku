from math import prod
from datetime import datetime

from sqlalchemy.sql.sqltypes import Date
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

def get_flight(noi_di=None, noi_den=None, time=None):
    flights = ChuyenBay.query
    
    
    
    if noi_di and noi_den and time:

        san_bay_di = SanBay.query.filter(DiaChi=noi_di).first()
        san_bay_den = SanBay.query.filter(DiaChi=noi_den).first()
        time = datetime.date(time)
        date = ChuyenBay.ThoiGianXuatPhat.date()
        flights = ChuyenBay.query.filter(Id_SanBay_Di=san_bay_di.id, 
                                        Id_SanBay_Den=san_bay_den.id,
                                        date=time).all()
    
    return flights


def get_newest_flight():
    return ChuyenBay.query.filter(ChuyenBay.ThoiGianXuatPhat.__gt__(datetime.now())).order_by(ChuyenBay.ThoiGianXuatPhat).limit(1)

def get_all_san_bay():
    return SanBay.query.all()