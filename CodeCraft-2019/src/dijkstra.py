# Dijkstra算法,用于预计算个点间的距离
 
def Dijkstra(G,source,INF=99999):
    book = set()
    minv = source.ID
    
    dis = dict((k,INF) for k in G.keys())
    dis[source] = 0
    
    while len(book)<len(G):
        book.add(minv)                                 
        for crossID,_ in G[minv].GetNeighbor():              
            weight = source.GetRoadLength(crossID)         
            if dis[minv] + weight < dis[crossID]:         
                dis[crossID] = dis[minv] + weight        
        
        new = INF                                      
        for v in dis.keys():
            if v in book: continue
            if dis[v] < new: 
                new = dis[v]
                minv = v
    return dis

def CalDistance(G):
    res={}
    for crossID,cross in G:
        res[crossID] = Dijkstra(G,cross)
    return res