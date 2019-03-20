# _*_ coding: utf-8 _*_
import io
import sys
import os
import re
import numpy as np
import Car
import Road
import Cross


class TextIO:
    def description(self):
        print("this is text io.")

    def __init__(self, path_car, path_road, path_cross, path_out):
        print("TextIO Constructor")
        self.path_car = path_car
        self.path_road = path_road
        self.path_cross = path_cross
        self.path_out = path_out

    def ReadAll(self):
        print("Read data")
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

    def Write(self, answer):
        print("Write data")
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
