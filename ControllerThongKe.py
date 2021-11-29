from models import *
from __init__ import db
from datetime import date
from ControllerTicket import TicketController
from ControllerNhapLich import NhapLichController
from sqlalchemy import exc


class ThongKeThangController:
    def xemThongKe(self,thang,nam):
        lichDAO = NhapLichController()
        listChuyenBay = lichDAO.timChuyenBayTheoThang(thang,nam)
        ticketDAO = TicketController() 
        lichDAO = NhapLichController()
        result = []
        for chuyenBay in listChuyenBay:
            tongVe = ticketDAO.tongVe(chuyenBay.id)
            tongTien = ticketDAO.tongTienVeBanDuoc(chuyenBay.id)
            tongGhe = lichDAO.tongSoLuongChoNgoi(chuyenBay.id)
            tk = {}
            tk['ChuyenBay']=chuyenBay.id
            tk['SoVe']= tongVe
            tk['Tyle']=0 if (tongVe==0 or tongGhe==0) else tongVe/tongGhe
            tk['DoanhThu']=tongTien
            result.append(tk)
        return result
        
    def updateNewIntoDatabase(self,thang,nam):
        listThongKeOld = DoanhThuThang.query.filter(DoanhThuThang.Thang==thang
                                 ,DoanhThuThang.Nam==nam).all()
        for tk in listThongKeOld:
            db.session.delete(tk)
        list= self.xemThongKe(thang,nam)
        for tk in list:
            dt = DoanhThuThang(TyLe=tk['Tyle'],DoanhThu=tk['DoanhThu'],
                               Id_ChuyenBay=tk['ChuyenBay'],
                               SoVeBanDuoc=tk['SoVe'],Thang=thang,Nam=nam)
            db.session.add(dt)
        try:
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False
    
class ThongKeNamController:
    
    def xemThongKe(self,nam):
        nhapLichDAO = NhapLichController()
        veDAO = TicketController()
        result=[]
        for thang in range(1,13):
            thongKe={}
            thongKe['Thang']=thang
            thongKe['Nam']=nam
            thongKe['SoChuyenBay']= nhapLichDAO.tongSoChuyenBayTrongThang(thang,nam)
            thongKe['DoanhThu']=veDAO.tongTienVeBanDuocTrongThang(thang,nam)
            tongSoVe =veDAO.tongSoVeTrongThang(thang,nam)
            tongSoghe = nhapLichDAO.tongSoLuongChoNgoiTrongThang(thang,nam)
            thongKe['Tyle']=0 if(tongSoVe==0 or tongSoghe==0) else tongSoVe/tongSoghe
            result.append(thongKe)
        return result
    def updateNewIntoDatabase(self,nam):
        listThongKeOld = DoanhThuNam.query.filter(DoanhThuNam.Nam==nam).all()
        for tk in listThongKeOld:
            db.session.delete(tk)
        list= self.xemThongKe(nam)
        for tk in list:
            dt = DoanhThuNam(TyLe=tk['Tyle'],DoanhThu=tk['DoanhThu'],
                             Thang=tk['Thang'],Nam=tk['Nam'],
                             SoChuyenBay=tk['SoChuyenBay'])
            db.session.add(dt)
        try:
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False        

def doanhThuNam(nam):
    thongKeDAO = ThongKeNamController()
    thongKeDAO.updateNewIntoDatabase(nam)
    return DoanhThuNam.query.filter(DoanhThuNam.Nam==nam).all()

def doanhThuThang(thang,nam):
    thongKeDao = ThongKeThangController()
    thongKeDao.updateNewIntoDatabase(thang,nam)
    return DoanhThuThang.query.filter(DoanhThuThang.Thang==thang
                                 ,DoanhThuThang.Nam==nam).all()
if(__name__=='__main__'):
    print(doanhThuNam(2021))
