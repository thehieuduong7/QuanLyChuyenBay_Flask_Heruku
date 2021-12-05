from sqlalchemy import exc
from __init__ import db,app
from models import *
import os
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
class KhachHangController():
    def insert(self,data):
        HoTenKH=data['HoTenKH']
        GioiTinh=data['GioiTinh']
        NamSinh=data['NamSinh']
        SDT=data['SDT']
        CMND=data['CMND']
        Email=data['Email']
        HinhAnh = data['HinhAnh']
        kh = KhachHang(HoTenKH=HoTenKH,GioiTinh=GioiTinh,
                       NamSinh=NamSinh,SDT=SDT,
                       CMND=CMND,Email=Email)
        db.session.add(kh)
        db.session.flush()
        db.session.refresh(kh)
        id= kh.id
        filename= 'hinhAnh'+str(id)+'.png'
        HinhAnh=self.saveImg(HinhAnh,filename)
        kh.HinhAnh=HinhAnh
        return kh
        
    
    def delete(self,kh):
        db.session.delete(kh)
        
    def search(self,search):
        search= "%"+search.strip()+"%"
        return KhachHang.query.filter(KhachHang.HoTenKH.like(search)).all()
    


    def allowed_file(self,filename):
	    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
    def saveImg(self,img,filename):
        if not (img and self.allowed_file(img.filename)):
            return None
        path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(path) 
        return path