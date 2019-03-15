# _*_ coding: utf-8 _*_
import numpy as np
import logging
           

class Cross:
    Roads = None
    RoadIDs = None
    Neighbor = None
    def __init__(self,ID,road1,road2,road3,road4):
        self.ID=ID
        self.RoadIDs = list([])
        self.RoadIDs.append(road1).append(road2).append(road3).append(road4)

    # 初始化道路对象
    def InitRoad(self,roadID,road):
        if self.Roads == None:
            self.Roads={}

        self.Roads[roadID,road]

    def GetRoad(self,roadID):
        if roadID in self.RoadIDs:
            return True,self.Roads[roadID]
        else:
            return False,None

    def GetNeighbor(self):
        if self.Neighbor == None:
            self.Neighbor={}
            for road in self.Roads:
                if road.startID == self.ID:
                    self.Neighbor[road.endID]=road.Cross[road.endID]
        return self.Neighbor
    
    def GetRoadLength(self,targetID):
        for road in self.Roads:
                if road.endID == targetID:
                    return road.GetWeight(targetID)
        