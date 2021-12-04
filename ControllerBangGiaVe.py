from __init__ import db
from models import *
class BangGiaVeController:
    def listBangGiaVe(self):
        return BangGiaVe.query.all()

    def insertBangGianVe(self,data):
        Id_ChuyenBay=data['Id_ChuyenBay']
        HangVe=data['HangVe']
        GiaVe = float(data['GiaVe'])
        SoGhe = int(data['SoGhe'])
        bangGia = BangGiaVe(Id_ChuyenBay=Id_ChuyenBay,
                    HangVe=HangVe,GiaVe=GiaVe,SoGhe=SoGhe)
        db.session.add(bangGia)
        db.session.flush()
        db.session.refresh(bangGia)
        return bangGia
