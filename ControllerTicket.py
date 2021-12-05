from flask.templating import render_template
from flask_mail import Message
from sqlalchemy.sql.expression import null
from ControllerKhachHang import KhachHangController
from ControllerNhapLich import NhapLichController
from ControllerQuyDinh import QuyDinhController
from models import *
from __init__ import db,app,mail
from datetime import date
from sqlalchemy import exc
import os
from datetime import datetime

class TicketController:
    def checkQuyDinhBanVe(self,Id_ChuyenBay,HangVe,soLuong):
        bangGia= BangGiaVe.query.filter(
            BangGiaVe.Id_ChuyenBay==Id_ChuyenBay,
            BangGiaVe.HangVe==HangVe
            ).first()
        if(bangGia==None): return False
        tongSoLuong = bangGia.SoGhe
        
        tongVeDaBan=  len(Ve.query.filter(Ve.Id_ChuyenBay==Id_ChuyenBay,
                                          Ve.HangVe==HangVe).all())
        if(tongSoLuong-tongVeDaBan<soLuong):
            return False
        return True
    def checkQuyDinhDatVe(self,idChuyenBay):
        quyDinhDAO = QuyDinhController()
        minDatVe = quyDinhDAO.ThoiGianDatVeToiThieu()
        minDatVe= int(minDatVe.NoiDung)
        chuyenBay = ChuyenBay.query.get(idChuyenBay)
        if(chuyenBay==None): return False
        ThoiGianXuatPhat = chuyenBay.ThoiGianXuatPhat
        diff_now = (ThoiGianXuatPhat-datetime.today()).days
        
        if(minDatVe>diff_now):
            return False
        return True
        
        
    def checkDuVe(self,idChuyenBay,hangVe,soLuongDat):
        SoLuongDaBan = len(Ve.query.filter_by(Id_ChuyenBay=idChuyenBay).all())
        TongSoLuongVe  = BangGiaVe.query.filter_by(Id_ChuyenBay=idChuyenBay,
                                        HangVe=hangVe).first().SoGhe
        if(TongSoLuongVe-SoLuongDaBan >= soLuongDat):
            return True
        else:
            return False
        

    def tongThanhToan(self,idChuyenBay,hangVe,soLuongDat):
        bangGia = BangGiaVe.query.filter_by(Id_ChuyenBay=idChuyenBay,
                                        HangVe=hangVe).first()
        if(bangGia==None): return None
        tongTien= bangGia.GiaVe * soLuongDat
        return tongTien
    def datVe(self,Id_ChuyenBay,HangVe,id_kh):
        ve =Ve(Id_ChuyenBay=Id_ChuyenBay,HangVe=HangVe,
            ThoiGianDatVe=datetime.now(),Id_KhachHang=id_kh)
        db.session.add(ve)
        db.session.flush()
        db.session.refresh(ve)
        return ve
    def sendTicketByMail(self,ListveMayBay):
        ListContent=[]
        for veMayBay in ListveMayBay:
            if(veMayBay==None):
                return False
            
            name = veMayBay.khachhang.HoTenKH
            id_ve=str(veMayBay.id) + '-' + str(veMayBay.khachhang.SDT) + '-' + str(veMayBay.Id_KhachHang)
            thoiGianDat= veMayBay.ThoiGianDatVe
            hangVe=veMayBay.HangVe
            
            chuyenBay = veMayBay.chuyenbay
            id_chuyenBay=chuyenBay.id
            sanBayDi=chuyenBay.sanbay_di.DiaChi+' ('+chuyenBay.sanbay_di.TenSB+')'
            sanBayDen=chuyenBay.sanbay_den.DiaChi+' ('+chuyenBay.sanbay_den.TenSB+')'
            bangGiaVe = BangGiaVe.query.filter_by(Id_ChuyenBay=id_chuyenBay,HangVe=hangVe ).first()
            giaVe=bangGiaVe.GiaVe
            
            email = veMayBay.khachhang.Email
            content = '''
                Hang hang khong gia re                                      Sai gon {time}
                                                        THONG TIN VE MAY BAY
                Khach hang: {name}
                Ma ve: {id_ve}
                Chuyen bay: {id_chuyenBay}
                San bay di: {sanBayDi:15} San bay den:{sanBayDen:20}
                Hang ve: {hangVe}
                Gia ve: {giaVe} dong
                Thoi gian dat: {thoiGianDat}
            '''
            contentSend = content.format(time=date.today(),name=name,id_ve=id_ve,
                id_chuyenBay=id_chuyenBay,sanBayDi=sanBayDi,sanBayDen=sanBayDen,hangVe=hangVe,
                giaVe=giaVe,thoiGianDat=thoiGianDat)
            msg={}
            msg['email']=email
            msg['contentSend']=contentSend
            ListContent.append(msg.copy())

        for content in ListContent:
            msg = Message(subject="Ve may bay gia re",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[content['email']],
                    body=content['contentSend'])
            mail.send(msg)
        return true
        


    def BanVeNhieuVe(self,Id_ChuyenBay,HangVe,list_kh):
        if(self.checkQuyDinhBanVe(
            Id_ChuyenBay,HangVe,len(list_kh))==False):
            return "Bán vé thất bại!!! Vi phạm quy định"
        kh_dao=KhachHangController()
        try:
            list_ve=[]
            for kh in list_kh:
                id=kh_dao.insert(kh).id
                ve = self.datVe(Id_ChuyenBay,HangVe,id)
                list_ve.append(ve)
            db.session.commit()
            self.sendTicketByMail(list_ve)
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return "Bán vé thất bại!!! Kiểm tra lại thông tin khách hàng!!!"
    
    def DatVeNhieuVe(self,Id_ChuyenBay,HangVe,list_kh):
        if(not self.checkQuyDinhDatVe(Id_ChuyenBay)):
            return False
        kh_dao=KhachHangController()
        try:
            list_ve=[]
            for kh in list_kh:
                id=kh_dao.insert(kh).id
                ve = self.datVe(Id_ChuyenBay,HangVe,id)
                list_ve.append(ve)
            self.sendTicketByMail(list_ve)
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False
        
        
    
    def tongVe(self,Id_ChuyenBay):
        return len(Ve.query.filter(Ve.Id_ChuyenBay==Id_ChuyenBay).all())
    
    def tongTienVeBanDuoc(self,Id_ChuyenBay):
        listVe = Ve.query.filter(Ve.Id_ChuyenBay==Id_ChuyenBay).all()
        tien =0
        for ve in listVe:
            bangGiaVe = BangGiaVe.query.filter_by(Id_ChuyenBay=ve.chuyenbay.id
                                                  ,HangVe=ve.HangVe ).first()
            giaVe=bangGiaVe.GiaVe
            tien+= 0 if (giaVe==None) else giaVe
        return tien
    
    def tongTienVeBanDuocTrongThang(self,thang,nam):
        nhapLichDAO = NhapLichController()
        list = nhapLichDAO.timChuyenBayTheoThang(thang,nam)
        tienVe = 0
        for i in list:
            tienVe += self.tongTienVeBanDuoc(i.id)
        return tienVe    
    
    def tongSoVeTrongThang(self,thang,nam):
        nhapLichDAO = NhapLichController()
        list = nhapLichDAO.timChuyenBayTheoThang(thang,nam)
        tongSoVe = 0
        for i in list:
            tongSoVe += self.tongVe(i.id)
        return tongSoVe    
    

if(__name__=="__main__"):
    dao = TicketController()
    ve = Ve.query.get(1)
    print(dao.sendTicketByMail(ve))
   # print(dao.checkQuyDinhBanVe(1,'Thuong',2))
        