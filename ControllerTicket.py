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
    def checkQuyDinh(self,idChuyenBay):
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
        if(bangGia==None): return None;
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
            id_ve=veMayBay.id
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

        with app.app_context():
            for content in ListContent:
                msg = Message(subject="Ve may bay gia re",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[content['email']],
                    body=content['contentSend'])
                mail.send(msg)
        return true
        


    def datNhieuVe(self,Id_ChuyenBay,HangVe,list_kh):
        kh_dao=KhachHangController()
        try:
            list_ve=[]
            for kh in list_kh:
                id=kh_dao.insert(kh).id
                ve = self.datVe(Id_ChuyenBay,HangVe,id)
                list_ve.append(ve)
            self.sendTicketByMail(list_ve)
            db.session.commit()
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
    
    def listBangGiaVe(self):
        return BangGiaVe.query.all()
from flask import render_template, request, redirect, session, jsonify


    


    

if(__name__=='__main__'):
    data_kh={}
    data_kh['HoTenKH']='hieu1'
    data_kh['GioiTinh']='nam'
    data_kh['NamSinh']='2001'
    data_kh['SDT']='16'
    data_kh['CMND']='16'
    data_kh['Email']='19110362@student.hcmute.edu.vn'
    data_kh['HinhAnh'] = None
    list_kh=[]
    list_kh.append(data_kh.copy())
    data_kh['HoTenKH']='hieu dem2'
    data_kh['GioiTinh']='nam'
    data_kh['NamSinh']='2001'
    data_kh['SDT']='17'
    data_kh['CMND']='17'
    data_kh['Email']='19110362@student.hcmute.edu.vn'
    data_kh['HinhAnh'] = None
    list_kh.append(data_kh.copy())
    ticDAO =TicketController()
    Id_ChuyenBay=1
    HangVe='Thuong'
    #print(ticDAO.datNhieuVe(1,'Thuong',list_kh))
    #print(ticDAO.datVe(1,'Thuong',26))
    khDAO = KhachHangController()
    #print(khDAO.insert(data_kh))
    #db.session.commit()
    '''
    with app.app_context():
        msg = Message(subject="Ve may bay gia re",
            sender=app.config.get("MAIL_USERNAME"),
            recipients=['19110362@student.hcmute.edu.vn'],
            body='test1')
        mail.send(msg)
    with app.app_context():
        msg = Message(subject="Ve may bay gia re",
            sender=app.config.get("MAIL_USERNAME"),
            recipients=['19110362@student.hcmute.edu.vn'],
            body='test2')
        mail.send(msg)
    '''
    ve1= Ve.query.get(24)
    ve2=Ve.query.get(25)
    print(ticDAO.sendTicketByMail([ve1,ve2]))
    print(ticDAO.sendTicketByMail([ve1,ve2]))
