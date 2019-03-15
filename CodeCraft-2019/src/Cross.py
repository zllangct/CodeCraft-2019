# _*_ coding: utf-8 _*_
import numpy as np
import logging
           

class Cross:
    Roads = None
    RoadIDs = None
    def __init__(self,crossID,road1,road2,road3,road4):
        self.crossID=crossID
        self.RoadIDs = list([])
        self.RoadIDs.append(road1).append(road2).append(road3).append(road4)


    # 初始化道路对象
    def InitRoad(self,roadID,road):
        if self.Roads == None:
            self.Roads={}

        self.Roads[roadID,road]
