# _*_ coding: utf-8 _*_ 
import textio

cars = list([])
crosses =list([])
roads=list([])

def Process(car_path,road_path,cross_path,answer_path):
    print("program start...")

    # Read input data
    input=textio.TextIO(car_path,road_path,cross_path,answer_path)
    roads,cars,crosses = input.ReadAll()    

    print("ssss")
