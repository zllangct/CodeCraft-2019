# _*_ coding: utf-8 _*_
import numpy as np
import logging
           

class Cross:
    
    def __init__(self,ID,road1,road2,road3,road4):
        self.ID=ID
        self.RoadIDs = list([])
        self.RoadIDs.append(road1)
        self.RoadIDs.append(road2)
        self.RoadIDs.append(road3)
        self.RoadIDs.append(road4)

        self.Roads = None
        self.Neighbor = None
    # 初始化道路对象
    def InitRoad(self,roadID,road):
        if self.Roads == None:
            self.Roads={}

        self.Roads[roadID]=road

    def GetRoad(self,roadID):
        if roadID in self.RoadIDs:
            return True,self.Roads[roadID]
        else:
            return False,None

    def GetNeighbor(self):
        if self.Neighbor == None:
            self.Neighbor={}
            for roadID in self.Roads.keys():
                road=self.Roads[roadID]
                if road.startID == self.ID:
                    self.Neighbor[roadID]=road.Cross[road.endID]
                elif road.endID == self.ID and road.isBothway==1:
                    self.Neighbor[roadID]=road.Cross[road.startID]

        return self.Neighbor
    
    def GetRoadLength(self,targetID):
        for roadID in self.Roads:
            road=self.Roads[roadID]
            if road.endID == targetID or (road.startID == targetID and road.isBothway ==1):
                return road.GetWeight(targetID)
    