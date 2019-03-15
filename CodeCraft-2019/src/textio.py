# _*_ coding: utf-8 _*_ 
import io
import sys
import os
import re

class TextIO:
    def description(self):
        print("this is text io.")
    
    def __init__(self,path_car,path_road,path_cross,path_out):
        print("TextIO Constructor")
        self.path_car=path_car
        self.path_road=path_road
        self.path_cross=path_cross
        self.path_out=path_out

    def ReadAll(self):
        print("Read data")
        with open(self.path_car,"r") as f1:
            lines=f1.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                args=[item for item in filter(lambda x:x!='',re.split("[(),]",line)) ] 
                print(args)

    def Write(self):
        print("Write data")

    