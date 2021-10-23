from flask import redirect
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView, form
from flask_login import current_user, logout_user

from __init__ import admin, db
from models import*


#view chứng thực, quyền cho phép đăng nhập vào view
class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin")
    def is_accessible(self):
        return current_user.is_authenticated
class DoanhThu(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render("admin/stats.html") 
class QuyDinh(BaseView):
    @expose('/')
    def index(self):
        return self.render("admin/rules.html")
    def is_accessible(self):
        return current_user.is_authenticated
        
class KhachHangModelView(AuthenticatedView): 
    #can_create = False
    can_export = True
    can_view_details = True
    #column_display_pk = True
    column_searchable_list = ('SDT', 'CMND', 'Email')
    column_filters = ('HoTenKH', 'NamSinh', 've')

    column_labels = dict(HoTenKH = "Họ Tên", 
                        GioiTinh = "Giới Tính", 
                        NamSinh = "Năm Sinh",
                        HinhAnh = "Hình Ảnh")
    column_descriptions = dict(HoTenKH = 'Đầy Đủ Họ Tên')
    can_set_page_size = True

class BangGiaVeModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_editable_list = ('SoGhe', 'GiaVe')

    column_default_sort = [('SoGhe', False), ('GiaVe', True)]
    column_filters = ('GiaVe', 'chuyenbay', "SoGhe", "HangVe")
    column_searchable_list = ('HangVe', 'SoGhe')

    column_labels = dict(HangVe = "Hạng",
                        GiaVe = "Giá",
                        SoGhe = "Số Ghế",
                        chuyenbay = "Chuyến Bay")
    column_descriptions = dict(HangVe = "Thường, Thương Gia,...",
                                GiaVe = "500.000VND - 1.000.000VND",
                                SoGhe = "Tối Đa 50")
    can_set_page_size = True

class MayBayModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_editable_list = ('TinhTrang', 'Ten')

    column_filters = ('TinhTrang', 'Ten', 'chuyenbay')
    column_searchable_list = ('Ten', 'Hang')

    column_labels = dict(Ten = "Tên Máy Bay",
                        Hang = "Hãng Hàng Không",
                        TinhTrang = "Tình Trạng")
    column_descriptions = dict(TinhTrang = "Sẵn Sàng/Không")
    can_set_page_size = True
    
class SanBayModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_editable_list = ('TenSB', 'DiaChi')

    column_filters = ('TenSB', 'chuyenbay_di', 'chuyenbay_den', 'trunggian')
    column_searchable_list = ('TenSB', 'DiaChi')

    column_labels = dict(TenSB = "Tên Sân Bay",
                        DiaChi = "Thành Phố")
    can_set_page_size = True
    
class ChuyenBayModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_editable_list = ('SoLuongChoNgoi', 'ThoiGianBay', 'Id_MayBay', 'ThoiGianXuatPhat')

    column_filters = ('SoLuongChoNgoi', 'ThoiGianBay', 'ThoiGianXuatPhat', 'trunggian', 've')
    column_searchable_list = ('Id_MayBay', 'SoLuongChoNgoi')

    column_labels = dict(ThoiGianXuatPhat = "Thời Gian Xuất Phát",
                        ThoiGianBay = "Thời Gian Bay",
                        SoLuongChoNgoi = "Số Ghế",
                        sanbay_di = "Sân Bay Đi",
                        sanbay_den = "Sân Bay Đến",
                        maybay = "Máy Bay")
    can_set_page_size = True

class TrungGianModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_editable_list = ('ThoiGianDung','GhiChu')
    column_default_sort = [('Id_ChuyenBay', True)]

    column_filters = ('ThoiGianDung', 'Id_ChuyenBay', 'Id_SanBay')
    column_searchable_list = ('ThoiGianDung', 'Id_ChuyenBay', 'Id_SanBay')

    column_labels = dict(ThoiGianDung = "Thời Gian Dừng",
                        GhiChu = "Ghi Chú",
                        sanbay_trunggian = "Sân Bay Trung Gian",
                        chuyenbay = "Chuyến Bay")
    can_set_page_size = True
class VeModelView(AuthenticatedView):
    can_export = True
    can_view_details = True

    column_filters = ('Id_ChuyenBay', 'Id_KhachHang', 'ThoiGianDatVe', 'HangVe')
    column_searchable_list = ('Id_KhachHang', 'HangVe', 'Id_ChuyenBay')

    column_labels = dict(HangVe = "Hạng Vé",
                        khachhang = "Tên Khách Hàng",
                        chuyenbay = "Chuyến Bay",
                        ThoiGianDatVe = "Thời Gian Đặt Vé")
    can_set_page_size = True
    
class NguoiDungModelView(AuthenticatedView):
    can_export = False
    column_searchable_list = ('TenDN', 'VaiTro', 'TenNguoiDung')
    column_editable_list = ('VaiTro', 'TenDN')
    
    column_labels = dict(TenDN = "Tên Đăng Nhập",
                        VaiTro = "Vai Trò",
                        TenNguoiDung = "Tên Người Dùng")
    column_choices = {
        'VaiTro': [
            ('A', 'Admin'),
            ('N', 'Nhân Viên Bán Vé'),
            ('K', 'Khách Hàng')
        ]}

#dmhahaa

admin.add_view(KhachHangModelView(KhachHang, db.session, name = "KhachHang"))
admin.add_view(SanBayModelView(SanBay, db.session, name = "SanBay"))
admin.add_view(MayBayModelView(MayBay, db.session, name = "MayBay"))
admin.add_view(ChuyenBayModelView(ChuyenBay, db.session, name = "ChuyenBay"))
admin.add_view(BangGiaVeModelView(BangGiaVe, db.session, name = "GiaVe"))
admin.add_view(VeModelView(Ve, db.session, name = "Ve"))
admin.add_view(TrungGianModelView(TrungGianChuyenBay, db.session, name ="TrungGian"))
admin.add_view(NguoiDungModelView(NguoiDung, db.session, name ="Users"))

admin.add_view(DoanhThu(DoanhThuThang, db.session, name = "DoanhThuThang"))
admin.add_view(DoanhThu(DoanhThuNam, db.session, name = "DoanhThuNam"))
admin.add_view(QuyDinh(name = "QuyDinh"))
admin.add_view(LogoutView(name = "DangXuat"))



