# _*_ coding: utf-8 _*_

class Car:
    def __init__(self,id,start,end,vmax,ptime):
        self.id=id
        self.start=start
        self.end=end
        self.vmax=vmax
        self.ptime=ptime

class Road:
    def __init__(self,id,len,vmax,chanCount,startID,endID,isBothway):
        self.id=id
        self.len=len
        self.vmax=vmax
        self.chanCount=chanCount
        self.startID=startID
        self.endID=endID
        self.isBothway=isBothway

class Cross:
    def __init__(self,crossroadsID,road1,road2,road3,road4):
        self.crossroadsID=crossroadsID
        self.road1=road1
        self.road2=road2
        self.road3=road3
        self.road4=road4