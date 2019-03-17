# -*- coding: utf-8 -*-

from heapq import heappush, heappop
from itertools import count
import golablData
import Road,Cross

def Heuristic(currentCross,target):
    return golablData.GlobalData.DistancePre[currentCross.ID][target.ID]

def astar(Map, source, target, heuristic=Heuristic):

    if heuristic is None:
        heuristic = lambda u, v:0

    push = heappush
    pop = heappop

    c = count()
    queue = [(0, next(c), source, 0, None)]
    enqueued = {}
    explored = {}

    while queue:
        _, __, curnode, dist, parent = pop(queue)
        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            
            if golablData.GlobalData.Debug:
                sstr=""
                for p in path:
                    sstr+=" "+str(p.ID)
                print(sstr)

            return path

        if curnode in explored:
            continue

        explored[curnode] = parent
        
        # debug ===================
        # if curnode.ID==60:
        #     print(curnode.ID)
        # temp = curnode
        # sstr=str(temp.ID)
        # while explored[temp] !=None:
        #     temp = explored[temp]
        #     sstr+=(" "+str(temp.ID))
        # print(sstr)
        # =========================

        for cross in curnode.GetNeighbor().values():
            if cross in explored:
                continue
            ncost = dist + cross.GetRoadByEndID(cross.ID).GetWeight(cross.ID)
            if cross in enqueued:
                qcost, h = enqueued[cross]
                if qcost <= ncost:
                    continue
            else:
                h = heuristic(cross, target)
            enqueued[cross] = ncost, h
            push(queue, (ncost + h, next(c), cross, ncost, curnode))



def astar_path_length(Map, source, target, heuristic=None):   
    path = astar(Map, source, target, heuristic)
    length = 0
    for i in range(0,len(path)-1):
        length+=path[i].GetRoadLength(path[i+1].ID)
    return length

