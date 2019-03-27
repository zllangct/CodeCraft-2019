#!/usr/bin/python
# -*- coding: utf-8 -*-
import simulator.textio as textio
from simulator.golablData import GlobalData
import simulator.CrossMap as CrossMap
import time
import copy,sys

sys.setrecursionlimit(1000000)

def Process(car_path, road_path, cross_path, answer_path):
    # print("program start...")

    # Read input data
    input = textio.TextIO(car_path, road_path, cross_path, answer_path)
    GlobalData.roads, GlobalData.cars, GlobalData.crosses = input.ReadAll()

    for road in GlobalData.roads:
        GlobalData.roadsByID[road.ID]=road
    for car in GlobalData.cars:
        GlobalData.carsByID[car.ID]=car
    for cross in GlobalData.crosses:
        GlobalData.crossesByID[cross.ID]=cross
    
    answers = input.ReadAnswer()
    # GenMap
    for road in GlobalData.roads:
        count = 0
        for cross in GlobalData.crosses:
            if cross.ID == road.startID:
                cross.InitRoad(road.endID, road)
                road.InitCross(cross.ID, cross)
                count += 1
            elif cross.ID == road.endID:
                road.InitCross(cross.ID, cross)
                cross.InitRoad(road.startID, road)
                count += 1

            if count >= 2:
                break

    GlobalData.Map = CrossMap.CrossMap(GlobalData.crosses)

    # cars enter garage
    for car in GlobalData.cars:
        car_answer = answers[car.ID]
        car.stime = int(car_answer[1])
        car.Path=[]
        curCross = car.GetStart()
        for roadID in car_answer[2]:
            road = GlobalData.roadsByID[int(roadID)]
            opCross = road.GetOppositeCross(curCross.ID)
            car.Path.append(opCross)
            curCross = opCross

        start = car.GetStart()
        start.EnterGarage(car)

    # garage sort
    for cross in GlobalData.crosses:
        cross.GarageSort()


def HandleRoad():
    # # print("handle roads")
    for road in GlobalData.roads:
        road.CarRun(True)


def HandleCross():
    for cross in GlobalData.crosses:
        cross.FrameComplete=False

    complete = len(GlobalData.crosses)
    count=0
    while(complete>0):
        count+=1
        for cross in GlobalData.crosses:
            if cross.FrameComplete:
                continue
            cross.CarRun(count)
            if cross.FrameComplete:
                complete-=1


def HandleGarage():
    for cross in GlobalData.crosses:
        cross.GoRoad()
