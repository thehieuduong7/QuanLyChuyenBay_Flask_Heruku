from __init__ import db,app
from models import *


class QuyDinhController:
    def ThoiGianBayToiThieu(self):
        return QuyDinh.query.filter(
            QuyDinh.QuyDinh=='ThoiGianToiThieu').first()
    def SoSanBayTrungGianToiDa(self):
        return QuyDinh.query.filter(
            QuyDinh.QuyDinh=='SoSanBayTrungGianToiDa'
        ).first()
    def ThoiGianDungToiThieu(self):
        return QuyDinh.query.filter(
            QuyDinh.QuyDinh=='ThoiGianDungToiThieu'
        ).first()
    def ThoiGianDungToiDa(self):
        return QuyDinh.query.filter(
            QuyDinh.QuyDinh=='ThoiGianDungToiDa'
        ).first()
    def ThoiGianDatVeToiThieu(self):
        return QuyDinh.query.filter(
            QuyDinh.QuyDinh=='ThoiGianDatVeToiThieu'
        ).first()
    def ThoiGianChinhSuaVeToiThieu(self):
        return QuyDinh.query.filter(
            QuyDinh.QuyDinh=='ThoiGianChinhSuaVeToiThieu'
        ).first()