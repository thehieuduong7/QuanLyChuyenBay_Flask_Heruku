from __init__ import db,app
from models import *

class KhachHangController():
    def insert(self,kh):
        db.session.add(kh)
        kh = KhachHang.query.order_by(KhachHang.id.desc()).first()
        return kh    
    
    def delete(self,kh):
        db.session.delete(kh)
        
    def search(self,search):
        search= "%"+search.strip()+"%"
        return KhachHang.query.filter(KhachHang.HoTenKH.like(search)).all()
    
    