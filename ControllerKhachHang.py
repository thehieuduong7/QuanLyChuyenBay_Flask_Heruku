from __init__ import db,app
from models import *

class KhachHangController():
    def insert(self,kh):
        db.session.add(kh)
        kh = KhachHang.query.order_by(KhachHang.id.desc()).first()
        return kh    
    
    def delete(self,kh):
        db.session.delete(kh)
        