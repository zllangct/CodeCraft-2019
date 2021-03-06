#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import os,re
import numpy as np
import Car
import Road 
import Cross


class TextIO:

    def __init__(self, path_car, path_road, path_cross, path_out):
        # print("TextIO Constructor")
        self.path_car = path_car
        self.path_road = path_road
        self.path_cross = path_cross
        self.path_out = path_out

    def ReadAll(self):
        # print("Read data")
        cars = list([])
        crosses = list([])
        roads = list([])

        # Read car data
        with open(self.path_car, "r") as f1:
            lines = f1.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                args = [item for item in filter(
                    lambda x:x != '', re.split("[(),\n]", line))]
                car = Car.Car(int(args[0]), int(args[1]), int(
                    args[2]), int(args[3]), int(args[4]))
                cars.append(car)

        # Read road data
        with open(self.path_road, "r") as f1:
            lines = f1.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                args = [item for item in filter(
                    lambda x:x != '', re.split("[(),\n]", line))]
                road = Road.Road(int(args[0]), int(args[1]), int(args[2]), int(
                    args[3]), int(args[4]), int(args[5]), int(args[6]))
                roads.append(road)

        # Read cross data
        with open(self.path_cross, "r") as f1:
            lines = f1.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                args = [item for item in filter(
                    lambda x:x != '', re.split("[(),\n]", line))]
                cross = Cross.Cross(int(args[0]), int(args[1]), int(
                    args[2]), int(args[3]), int(args[4]))
                crosses.append(cross)

        return roads, cars, crosses
    def ReadAnswer(self):
        # print("Read data")
        cars = list([])
        crosses = list([])
        roads = list([])

        # Read car data
        with open(self.path_car, "r") as f1:
            lines = f1.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                args = [item for item in filter(
                    lambda x:x != '', re.split("[(),\n]", line))]
                car = Car.Car(int(args[0]), int(args[1]), int(
                    args[2]), int(args[3]), int(args[4]))
                cars.append(car)
                
    def Write(self, answer):
        # print("Write data")
        with open(self.path_out, "wt") as f:
            # for line in answer:
            #     sstr =[]
            #     for c in line:
            #         if len(sstr)==0 :
            #             sstr = sstr+c
            #         else:
            #             sstr = sstr+","
            #             sstr = sstr+c
            #     sstr = "("+ sstr+")"
            #     f.write(sstr)
            f.write(answer)

    def ReadTemp(self,temp_path):
        if not os.path.exists(temp_path):
            return 1000000,1000000,0,500
        with open(temp_path, "r") as f1:
            lines = f1.readlines()
            keys= lines[0].split(",")
            return int(keys[0]),int(keys[1]),int(keys[2]),int(keys[3])

    def WriteTemp(self,temp_path,time,total_time,seed,maxc):
        with open(temp_path, "wt") as f:
            f.write("%d,%d,%d,%d"%(time,total_time,seed,maxc))