# _*_ coding: utf-8 _*_ 
import textio
from golablData import GlobalData
import CrossMap,dijkstra

def Process(car_path,road_path,cross_path,answer_path):
    print("program start...")

    # Read input data
    input=textio.TextIO(car_path,road_path,cross_path,answer_path)
    GlobalData.roads,GlobalData.cars,GlobalData.crosses = input.ReadAll()    

    # GenMap
    for road in GlobalData.roads:
        count = 0
        for cross in GlobalData.crosses:
            if cross.ID== road.startID:
                road.InitCross(cross.ID,cross)
                cross.InitRoad(road.startID,road)
                count+=1
            elif cross.ID==road.endID:
                road.InitCross(cross.ID,cross)
                cross.InitRoad(road.endID,road)
                count +=1

            if count >=2:
                break

    GlobalData.Map=CrossMap.CrossMap(GlobalData.crosses)
    
    # calculate distance
    GlobalData.DistancePre = dijkstra.CalDistance(GlobalData.Map) 
    
    # Main logic loop 
    GlobalData.state = 1
    frameCount = 0
    while GlobalData.state == 1:
        frameCount+=1
        GlobalData.CurrentTime=frameCount
        Frame()
        
    # Write output data

def Frame():
    print("Current frame:",GlobalData.CurrentTime)
    
    # HandleRoad()
    # HandleCross()
    # HandleGarage()
    

# def HandleRoad():
#     print(timeFrame)
#     # for road in GlobalData.roads:
        

# def HandleCross():
#     print()

# def HandleGarage():
#     print()
