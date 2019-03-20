# Dijkstra算法,用于预计算个点间的距离


def Dijkstra(G, source, INF=99999):
    book = set()
    minv = source.ID

    dis = dict((k, INF) for k in G.keys())
    dis[source.ID] = 0

    while len(book) < len(G):
        book.add(minv)
        for crossID in G[minv].GetNeighbor():
            weight = G[minv].GetRoadLength(crossID)
            if weight == None:
                weight = INF
            if dis[minv] + weight < dis[crossID]:
                dis[crossID] = dis[minv] + weight

        new = INF
        for v in dis.keys():
            if v in book:
                continue
            if dis[v] < new:
                new = dis[v]
                minv = v
    return dis


def CalDistance(G):
    res = {}
    for crossID in G.Crosses.keys():
        res[crossID] = Dijkstra(G.Crosses, G[crossID])
    return res
