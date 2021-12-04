from operator import and_
from ControllerBangGiaVe import BangGiaVeController
from ControllerNhapTrungGian import TrungGianController
from ControllerQuyDinh import QuyDinhController
from __init__ import db,app
from models import *
from flask import request
from flask import jsonify
import json
from sqlalchemy import exc

def listSanBay():
    return SanBay.query.all().last()
class NhapLichController():
    def checkQuyDinh(self,data):

        ThoiGianBay=int(data['ThoiGianBay'])
        
        quyDinhDAO =QuyDinhController()
        minTimeBay = int(quyDinhDAO.ThoiGianBayToiThieu().NoiDung)
        if(ThoiGianBay<minTimeBay): return False
        ListTrungGian = data['ListTrungGian']
        trungGianDAO = TrungGianController()
        if(not trungGianDAO.checkQuyDinh(ListTrungGian)):
            return False
        return True
        
        
    
    def insertChuyenBay(self,data):
        Id_MayBay=data['Id_MayBay']
        Id_SanBay_Di=data['Id_SanBay_Di']
        Id_SanBay_Den=data['Id_SanBay_Den']
        ThoiGianXuatPhat=data['ThoiGianXuatPhat']
        ThoiGianBay=data['ThoiGianBay']
        SoLuongChoNgoi=data['SoLuongChoNgoi']
        chuyenBay= ChuyenBay(Id_MayBay=Id_MayBay,Id_SanBay_Di=Id_SanBay_Di,
        Id_SanBay_Den=Id_SanBay_Den,ThoiGianXuatPhat=ThoiGianXuatPhat,
        ThoiGianBay=ThoiGianBay,SoLuongChoNgoi=SoLuongChoNgoi)
        db.session.add(chuyenBay)
        db.session.flush()
        db.session.refresh(chuyenBay)
        return chuyenBay
    
    def nhapLich(self,data):
        if(self.checkQuyDinh(data)==False): return "Nhập lịch lỗi!! Nhập sai quy định"
        trungGianDAO = TrungGianController()
        bangGiaDAo =BangGiaVeController()
        ListTrungGian = data['ListTrungGian']
        ListHangVe = data['ListHangVe']
        try:
            chuyenBay=self.insertChuyenBay(data)
            for trungGian in ListTrungGian:
                data['Id_ChuyenBay']=chuyenBay.id
                data['Id_SanBay'] = trungGian['Id_SanBay']
                data['ThoiGianDung'] = trungGian['ThoiGianDung']
                data['GhiChu']=trungGian['GhiChu']
                trungGianDAO.insert(data.copy())
            for hangVe in ListHangVe:
                data['Id_ChuyenBay']=chuyenBay.id
                data['HangVe'] = hangVe['HangVe']
                data['GiaVe'] = hangVe['GiaVe']
                data['SoGhe']=hangVe['SoGhe']
                bangGiaDAo.insertBangGianVe(data.copy())
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return 'Nhập lịch lỗi!!! Thông tin đã tồn tại'

        
    def timChuyenBayTheoThang(self,thang,nam):
        from calendar import monthrange
        day_start = str(nam)+'-'+str(thang)+'-'+'1'
        num_days =monthrange(nam, thang)[1] 
        day_end = str(nam)+'-'+str(thang)+'-'+str(num_days)
        list = ChuyenBay.query.filter(
            and_(ChuyenBay.ThoiGianXuatPhat <= day_end, ChuyenBay.ThoiGianXuatPhat >= day_start)
        ).all()
        return list
    
    def tongSoLuongChoNgoi(self,id_chuyenBay):
        listQuanlyVe = BangGiaVe.query.filter(BangGiaVe.Id_ChuyenBay==id_chuyenBay).all()
        tongSo=0
        for i in listQuanlyVe:
            tongSo+=i.SoGhe
        return tongSo
    
    def tongSoLuongChoNgoiTrongThang(self,thang,nam):
        listChuyenBay= self.timChuyenBayTheoThang(thang,nam)
        tongSoChoNgoi=0
        for i in listChuyenBay:
            tongSoChoNgoi+=self.tongSoLuongChoNgoi(i.id)
        return tongSoChoNgoi

    def tongSoChuyenBayTrongThang(self,thang,nam):
        return len(self.timChuyenBayTheoThang(thang,nam))




@app.route('/chuyenBay-api',methods=['POST'])
def postChuyenBay():
    data = json.loads(request.data)
    return jsonify(data)


@app.route('/chuyenBay-api',methods=['Delete'])
def delChuyenBay():
    body = json.loads(request.data)
    print(body['hello'])
    return jsonify(body)

#@app.route('/chuyenBay-api',methods=['GET'])
#def updChuyenBay():
   # r =request.
if __name__ == '__main__':

     #  Id_MayBay=data['Id_MayBay']
    # Id_SanBay_Di=data['Id_SanBay_Di']
      #  Id_SanBay_Den=data['Id_SanBay_Den']
      #  ThoiGianXuatPhat=data['ThoiGianXuatPhat']
      #  ThoiGianBay=data['ThoiGianBay']
     #   SoLuongChoNgoi=data['SoLuongChoNgoi']
      #  ListtrungGian = ['listTrungGian']
          #    Id_SanBay = data['Id_SanBay']
       # ThoiGianDung = data['ThoiGianDung']
      #  GhiChu = data['GhiChu']
    data = {
        'Id_MayBay': 1,'Id_SanBay_Di': 1,
        'Id_SanBay_Den': 2,'ThoiGianXuatPhat': 1,
        'ThoiGianBay': 1,'SoLuongChoNgoi': 1,
        'ListrungGian': [
            {
                'Id_SanBay':1,
                'ThoiGianDung':2,
                'GhiChu':'khong'
            },
            {
                'Id_SanBay':2,
                'ThoiGianDung':2,
                'GhiChu':'khong'
            }
        ]
    }
    nhapDAO = NhapLichController()
    #print(nhapDAO.checkData(data))
    #print(data)
    
