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
                cross.InitRoad(road.endID,road)
                if road.isBothway==1:
                    road.InitCross(cross.ID,cross)
                    count+=1
            elif cross.ID==road.endID:
                road.InitCross(cross.ID,cross)
                if road.isBothway==1:
                    cross.InitRoad(road.startID,road)
                count +=1

            if (road.isBothway==1 and count >=2) or (road.isBothway==0 and count>=1):
                break

    GlobalData.Map=CrossMap.CrossMap(GlobalData.crosses)
    
    # calculate distance
    GlobalData.DistancePre = dijkstra.CalDistance(GlobalData.Map) 

    # cars enter garage
    for car in GlobalData.cars:
        start = car.GetStart()
        start.EnterGarage(car)

    # garage sort
    for cross in GlobalData.crosses:
        cross.GarageSort()

    # Main logic loop 
    RunV = 0.0
    CompPre = 0
    CarMax = 0 

    GlobalData.state = 1
    frameCount = 0
    while GlobalData.state == 1:
        frameCount+=1
        GlobalData.CurrentTime=frameCount
        Frame()

        

        # 信息统计
        roadInfo = GlobalData.StateInfo["RoadInfo"]["CarCount"]
        roadCarCount = 0
        for _carCount in roadInfo.values():
            roadCarCount+=_carCount
        GlobalData.Car_Road = roadCarCount
        print("当前道路中的车辆：%d" % roadCarCount)

        crossInfo = GlobalData.StateInfo["CrossInfo"]["CarCount"]
        crossCarCount = 0
        for _carCount in crossInfo.values():
            crossCarCount+=_carCount
        GlobalData.Car_Garage =crossCarCount


        print("车库中的车辆：%d" % crossCarCount)

        print("到达终点车辆：%d"%GlobalData.ComplateCount)

        v = GlobalData.ComplateCount-CompPre
        if v > RunV:
            CarMax = roadCarCount
            RunV = v
        CompPre = GlobalData.ComplateCount

        print("到达量：%d  最大值：%d  最大值时道路承载量：%d"%(v,RunV,CarMax))
    # Write output data
    input.Write(GlobalData.Result)


def Frame():
    print("Current frame:"+str(GlobalData.CurrentTime))
    
    HandleRoad()
    HandleCross()
    HandleGarage()
    

def HandleRoad():
    # print("handle roads")
    for road in GlobalData.roads:
        road.CarRun()
        

def HandleCross():
    
    for cross in GlobalData.crosses:
        cross.CarRun()

def HandleGarage():
    max = 2000 - GlobalData.Car_Road
    if GlobalData.Car_Road > 2000:
        max =0  
    else:   
        if max <=0 :
            max =64

    every = int(max / 64.0)

    # every = 1

    for cross in GlobalData.crosses:
        cross.GoRoad(every)
