from flask_mail import Message
from sqlalchemy.sql.expression import null
from ControllerKhachHang import KhachHangController
from ControllerNhapLich import NhapLichController
from models import *
from __init__ import db,app,mail
from datetime import date

class TicketController:
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
            ThoiGianDatVe=date.today(),Id_KhachHang=id_kh)
        db.session.add(ve)
        ve = Ve.query.order_by(Ve.id.desc()).first()
        return ve
    def sendTicketByMail(self,veMayBay):
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
        with app.app_context():
            msg = Message(subject="Ve may bay gia re",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[email],
                body=contentSend)
            mail.send(msg)
            return true

    def datNhieuVe(cls,Id_ChuyenBay,HangVe,list_kh):
        kh_dao = KhachHangController()
        for kh in list_kh:
            id= kh_dao.nhapThongTinKhachHang(kh).id
            ve = cls.datVe(Id_ChuyenBay,HangVe,id)
            if(ve==None):
                db.session.rollback()
                return False
            cls.sendTicketByMail(ve)
        db.session.commit()
        return True
    
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


if(__name__=='__main__'):
    #kh=KhachHang.query.filter(KhachHang.HoTenKH=='ten').first()
    #print(type(kh.NamSinh))
    
    #ve = Ve.query.get(1)
    #sendTicket(ve)
   # chuyen = ChuyenBay.query.get(1)
   # print(dir(chuyen))
    #sanBay = SanBay(TenSB='h',DiaChi='h')
   # db.session.add(sanBay)
    #lay = SanBay.query.filter_by(TenSB='h').first()
    #print(lay.id)
    
    #kh = KhachHang(
         ##         HoTenKH=data[0],GioiTinh =data[0],NamSinh =data[0]
             #      ,SDT =data[0], CMND =data[0],HinhAnh=data[0],Email = data[0])
             
    #data = ['ten','name','2021-10-23','30003','40005',null,'19110362@student.hcmute.edu.vn']
    #print(nhapThongTinKhachHang(data))
    #nhapThongTinKhachHang()
    #print(TongThanhToan(1,'Thuong',2))
    print(TicketController().tongTienVeBanDuoc(1))
