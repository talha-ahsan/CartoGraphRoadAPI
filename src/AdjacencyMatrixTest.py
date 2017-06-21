import datetime
import numpy as np
origVert = open('../simpleData/Original Vertices.txt', "r")
semanticTree = open('../simpleData/NewSemanticTree.txt', "r")


def getPath(childEdgeId, edgeDict, frontStack = [], backStack = []):
    frontStack.append(edgeDict[childEdgeId][0])
    backStack.insert(0, edgeDict[childEdgeId][1])
    if(len(edgeDict[childEdgeId]) == 4):
        #we still have parents!
        parentID = edgeDict[childEdgeId][2]
        return getPath(parentID, edgeDict, frontStack, backStack)
    elif(len(edgeDict[childEdgeId]) == 3):
        #merge stacks:
        for element in backStack:
            frontStack = frontStack.append(element)
        return frontStack

def prunePath(unprunedPath):
    for i in range(0, len(unprunedPath)-2):
        #note sure if this works
        edgeWeight = outboundPaths[unprunedPath[i]][unprunedPath[i+1]][1]
        if int(edgeWeight) < 50:
            del unprunedPath[i]
            i-=1
    return unprunedPath

def getViewPortPaths(xmin, xmax, ymin, ymax, vertices, outboundPaths, inboundPaths, edgeDict):
    pointsinPort = []
    outpathsToMine = []
    inpathsToMine = []
    for point in vertices:
        if xmax > float(vertices[point][0]) > xmin and ymin < float(vertices[point][1]) < ymax:
            pointsinPort.append(point) #points in port is an array of pointIDs which are strings.
            try:
                for dest in outboundPaths[point]:
                    outpathsToMine.append((point, dest)) #outpaths and inpaths include points and dest of edges we want to reconstruct
            except KeyError:
                pass
            try:
                for src in inboundPaths[point]:
                    p = vertices[src]
                    if (xmax < float(p[0]) or float(p[0]) < xmin) or (ymin > float(p[1]) or float(p[1]) > ymax):
                        inpathsToMine.append([src, point])
            except KeyError:
                pass

   # print("Points in the viewport: ")
    #print(pointsinPort)
    paths = []
    print("Finding paths now. Paths to do: " + str(len(inpathsToMine) +len(outpathsToMine)))
    for path in inpathsToMine: #path[0] = src, path[1] = dest

        paths.append(getPath(inboundPaths[path[1]][path[0]][0], edgeDict,[], []))
       # print(path)
        #print(inboundPaths[path[1]])
        if(len(paths) % 100000 == 0):
            print(len(paths))
    for path in outpathsToMine:
        paths.append(getPath(outboundPaths[path[0]][path[1]][0], edgeDict))
        if len(paths) % 100000 == 0:
            print(len(paths))
    return paths

oldTime = datetime.datetime.now()
origVert = [x.rstrip() for x in origVert]
semanticTree = [x.rstrip() for x in semanticTree]
dictFormingSemanticTree = semanticTree
del(origVert[0])
vertices = {}
#Creates a dict with vertex ID as key, then x/y coordinates as values in array list.
for line in origVert:
    a,b,c = line.split(" ")
    vertices[a] = [b,c]


outboundPaths = {}
edgeDictionary = {}
#inboundPaths is a dictinary where the key is a vertex and the values are an array which is composed of all the values which have roads going into the key value. This is the reverse of outboundPaths where the key has outbound roads to the values
inboundPaths = {}
#Todo: set pairings to be the new fangled dictionary thingamabobber
pairings = []
print("Making the three dictionaries now!")
for line in dictFormingSemanticTree:
    elements = line.split(" ")
    edgeDictionary[elements[0]] = elements[1:] #Edge ID as key,  [src, dest, parent, weight] as vals
    #if both src and dst are in orig Vertices:
    if(elements[1] in vertices and elements[2] in vertices): #elements = [edgeId, src, dst, parent, weight]
        #todo: reverify this makes sense. elements[1] is src, elements[2] is dest
        pairings.append((elements[1], elements[2]))
        if len(elements) == 4: #here there's EdgeID, src, dest, weight, here we ARE at the parent
            if elements[1] in outboundPaths:
                outboundPaths[elements[1]].update({elements[2]: [elements[0], elements[3]]})
            else:
                outboundPaths[elements[1]] = {elements[2]: [elements[0], elements[3]]}
            if elements[2] in inboundPaths:
                inboundPaths[elements[2]].update({elements[1]:[elements[0], elements[3]]})
            else:
                inboundPaths[elements[2]] = {elements[1]:[elements[0], elements[3]]}
        elif len(elements) == 5: #here we are still at a child and have to append the parent. format: Src key -> dest Key -> [EdgeId, Weight, Parent if exists], if path[src][dest].size = 3, we gotta keep going, if =2, we at end
            if elements[1] in outboundPaths:
                outboundPaths[elements[1]].update({elements[2]: [elements[0], elements[4], elements[3]]})
            else:
                outboundPaths[elements[1]] = {elements[2]: [elements[0], elements[4], elements[3]]}
            if elements[2] in inboundPaths:
                inboundPaths[elements[2]].update({elements[1]: [elements[0], elements[4], elements[3]]})
            else:
                inboundPaths[elements[2]] = {elements[1]: [elements[0], elements[4], elements[3]]}


print("Done setting up stuff, now pairing and pathing")
paths = (getViewPortPaths(-20, 20, -20, 20, vertices, outboundPaths,inboundPaths, edgeDictionary))
print(len(paths))
print("All roads generated. Have a great day! (hehe xd)")
print(paths[12])
print(paths[199])
print(paths[400])
#keys = inboundPaths.keys()
#print(inboundPaths[keys[0]])

#print(outboundPaths[keys[0]])
newtime = datetime.datetime.now()
print("Time elapsed: " + str(newtime-oldTime))
#New implementation preferred: dict[src:dict[dest:[edgeId, weight, ParentID]]] BUT how do we find inbound edges quickly? do we make a reversed one?