# _*_ coding: utf-8 _*_
import numpy as np
import logging

class CarState:
    Null = -1
    WaitingRun = 1
    Waiting =2
    ActionEnd = 3


class Car:
    # CurrentRoad = None
    # CurrentChannel = None
    Path=None
    PathPassing = list([])
    
    def __init__(self,id,start,end,vmax,ptime):
        self.id=id
        self.start=start
        self.end=end
        self.vmax=vmax
        self.ptime=ptime

        self.state = CarState.Null

    # def NextRoad(self,cross):
