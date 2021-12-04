from ControllerQuyDinh import QuyDinhController
from __init__ import db
from models import *

class TrungGianController:
    def checkQuyDinh(self,ListTrungGian):
        quyDinhDAO = QuyDinhController()
        maxLen = int(quyDinhDAO.SoSanBayTrungGianToiDa().NoiDung)
        thoiGianDungMin = int(quyDinhDAO.ThoiGianDungToiThieu().NoiDung)
        thoiGianDungMax = int(quyDinhDAO.ThoiGianDungToiDa().NoiDung)
        if(len(ListTrungGian)>maxLen):
            return False
        for tg in ListTrungGian:
            if(tg['ThoiGianDung']<thoiGianDungMin or 
               tg['ThoiGianDung']>thoiGianDungMax):
                return False
        return True
            
            
    def insert(self, data):
        Id_SanBay = data['Id_SanBay']
        Id_ChuyenBay =data['Id_ChuyenBay']
        ThoiGianDung =data['ThoiGianDung']
        GhiChu=data['GhiChu']
        trungGian = TrungGianChuyenBay(Id_SanBay=Id_SanBay,
        Id_ChuyenBay=Id_ChuyenBay,ThoiGianDung=ThoiGianDung,GhiChu=GhiChu)
        db.session.add(trungGian)
        db.session.flush()
        db.session.refresh(trungGian)
    
    


    