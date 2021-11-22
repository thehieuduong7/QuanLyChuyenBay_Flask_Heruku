from math import prod
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