from py2neo import Graph, Path
import json

'''''
DICT STRUCTURE
name
parent
connections:
    weight
    parent
    name
    keywords []
    relationshipTypes []
    opt=>semanticRelationships
'''''

def list_merge(l1, l2):
    mynewlist = []
    namesA = []
    namesB = []
    for item in l1:
        namesA.append(item['name'])
    for item in l2:
        namesB.append(item['name'])
    namesA = list(set(namesA))
    namesB = list(set(namesB))
    resA = set(namesB) - set(namesA)
    resA = list(resA)
    resB = set(namesA) - set(namesB)
    resB = list(resB)
    for item in l2:
        for name in resA:
            if item["name"] == name:
                mynewlist.append(item)
    for item in l1:
        for name in resB:
            if item["name"] == name:
                mynewlist.append(item)
    for item in l1:
        for obj in l2:
            if item['name'] == obj['name']:
                mycheck = "true"
                for check in mynewlist:
                    if obj['name'] == check['name']:
                        mycheck = "false"
                if mycheck == "true":
                    anobj = {}
                    anobj['name'] = item['name']
                    connectionList = item['connections']
                    toBeComparedList = obj['connections']
                    theconnections = []
                    namesC = []
                    namesD = []
                    for comp in connectionList:
                        namesC.append(comp['name'])
                    for comp in toBeComparedList:
                        namesB.append(comp['name'])
                    namesC = list(set(namesC))
                    namesD = list(set(namesD))
                    resuA = set(namesD) - set(namesC)
                    resuA = list(resuA)
                    resuB = set(namesC) - set(namesD)
                    resuB = list(resuB)
                    for i in toBeComparedList:
                        for name in resuA:
                            if i["name"] == name:
                                theconnections.append(i)
                    for i in connectionList:
                        for name in resuB:
                            if i["name"] == name:
                                theconnections.append(i)
                    for i in connectionList:
                        for o in toBeComparedList:
                            if i['name'] == o['name']:
                                nweight = (i['weight'] + o['weight'])/2
                                mykeys = list(set(i['keywords'] + o['keywords']))
                                myrels = list(set(i['relationshiptypes'] + o['relationshiptypes']))
                                nam = i['name']
                                semRels = []
                                mergedConnection = {}
                                if "semanticrelationships" in i:
                                    semRels = i["semanticrelationships"]
                                mergedConnection = {"name": nam, "weight": nweight, "keywords": mykeys, "relationshiptypes": myrels, "semanticrelationships": semRels}
                                theconnections.append(mergedConnection)
                    anobj['connections'] = theconnections
                    mynewlist.append(anobj)
    return mynewlist

def list_enhance(li):
    nameset = []
    for item in li:
        nameset.append(item['name'])
    nameset = list(set(nameset))
    
    for item in li:
        myconns = item['connections']
        for obj in myconns:
            if obj['name'] not in nameset:
                li.append({'name':obj['name'], 'connections':[]})
    return li

#graphURL = 'http://hobby-ipadfcfgpodkgbkedbggakbl.dbs.graphenedb.com:24789'
#graphUser = 'rheauser'
#graphPass = 'b.tvYI5zZ7SWCQ.l04N5jzsNkbFCzFf'

graphURL = 'http://127.0.0.1:7474'
graphUser = ''
graphPass = ''

g = Graph(graphURL, user=graphUser, password=graphPass)

#authenticate("hobby-ipadfcfgpodkgbkedbggakbl.dbs.graphenedb.com:24789", "rheauser", "b.tvYI5zZ7SWCQ.l04N5jzsNkbFCzFf")
#g = Graph("http://hobby-ipadfcfgpodkgbkedbggakbl.dbs.graphenedb.com:24789", bolt = False)

#authenticate("hobby-ipadfcfgpodkgbkedbggakbl.dbs.graphenedb.com:24780", "rheauser", "b.tvYI5zZ7SWCQ.l04N5jzsNkbFCzFf")
#g = Graph("bolt://hobby-ipadfcfgpodkgbkedbggakbl.dbs.graphenedb.com:24786", user="rheauser", password="b.tvYI5zZ7SWCQ.l04N5jzsNkbFCzFf", bolt=True, secure = True, http_port = 24789, https_port = 24780)
#g = Graph("https://hobby-ipadfcfgpodkgbkedbggakbl.dbs.graphenedb.com:24789", bolt = False)

def getontologydata():
    firstdict = g.run('MATCH (n)-[nk]->(k:Keyword)-[r]->(ke:Keyword)-[kep]->(p) WHERE NOT n:Keyword AND NOT p:Keyword  WITH n,nk,k,r,ke,kep,p, CASE WHEN nk.rakeScore is null THEN 0.0 ELSE nk.rakeScore END AS firstRakeScore WITH n,nk,k,r,ke,kep,p,firstRakeScore, CASE WHEN kep.rakeScore is null THEN 0.0 ELSE kep.rakeScore END AS secondRakeScore WITH n,nk,k,r,ke,kep,p,firstRakeScore,secondRakeScore, CASE WHEN r.semanticWeight is null THEN 0.0 ELSE r.semanticWeight END AS semanticW WITH n, p, collect({keywordA: k.name, relType: type(r), keywordB: ke.name, weight: firstRakeScore + semanticW + secondRakeScore}) as keyRels  WITH n, p, keyRels, reduce(totalWeight = 0, x IN keyRels| totalWeight + x.weight) AS completeWeight WITH n, p, keyRels, completeWeight, extract(item IN keyRels|item.relType) AS relTypes WITH n, p, keyRels, completeWeight, relTypes, extract(item IN keyRels| item.keywordA) AS keywordsA WITH n, p, keyRels, completeWeight, relTypes, keywordsA, extract(item IN keyRels| item.keywordB) AS keywordsB WITH n, p, keyRels, completeWeight, relTypes, keywordsA + keywordsB AS kkeywords WITH n, p, keyRels, completeWeight, relTypes, kkeywords, CASE  WHEN "Flow" IN LABELS(p) THEN p.title  WHEN "CoreFlow" IN LABELS(p) THEN p.title WHEN "LeadershipBehaviour" IN LABELS(p) THEN p.title WHEN "Risk" IN LABELS(p) THEN p.title WHEN "UPLCPhase" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, keyRels, completeWeight, connectedTitle, relTypes, kkeywords, CASE WHEN "Flow" IN LABELS(p) THEN "PARTOFCOREFLOW"  WHEN "CoreFlow" IN LABELS(p) THEN "SUBCLASSOF" WHEN "LeadershipBehaviour" IN LABELS(p) THEN "CONSTITUTES" WHEN "Risk" IN LABELS(p) THEN "OFRISKAREA" WHEN "UPLCPhase" IN LABELS(p) THEN "PHASEOF" END AS preltype WITH n, p, keyRels, completeWeight, connectedTitle, relTypes, kkeywords, preltype  MATCH (p)-[pt]->(parentNode) WHERE TYPE(pt) CONTAINS preltype WITH n, p, parentNode, keyRels, completeWeight, connectedTitle, relTypes, kkeywords, CASE WHEN "CoreFlow" IN LABELS(parentNode) THEN parentNode.title WHEN "LeadershipTopic" IN LABELS(parentNode) THEN parentNode.title WHEN "LeadershipTeamInteractionArea" IN LABELS(parentNode) THEN parentNode.name WHEN "LeadershipBehaviour" IN LABELS(parentNode) THEN parentNode.title WHEN "Risk" IN LABELS(parentNode) THEN parentNode.title WHEN "RiskArea" IN LABELS(parentNode) THEN parentNode.name WHEN "UPLifeCycle" IN LABELS(parentNode) THEN parentNode.name END AS pparent WITH n, p, pparent, keyRels, completeWeight, connectedTitle, relTypes, kkeywords, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(p) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(p) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(p) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(p) THEN "solarbird.upphase" END AS connectedTitleExtension WITH n, {name: connectedTitleExtension + "." + pparent + "." + connectedTitle, parent: pparent, weight: completeWeight, keywords: kkeywords, relationshipTypes: relTypes, semanticConnections: keyRels} as relatedNode  WITH n, relatedNode, CASE  WHEN "Flow" IN LABELS(n) THEN n.title  WHEN "CoreFlow" IN LABELS(n) THEN n.title WHEN "LeadershipBehaviour" IN LABELS(n) THEN n.title WHEN "Risk" IN LABELS(n) THEN n.title WHEN "UPLCPhase" IN LABELS(n) THEN n.name END AS mainTitle WITH n, relatedNode, mainTitle, CASE WHEN "Flow" IN LABELS(n) THEN "PARTOFCOREFLOW"  WHEN "CoreFlow" IN LABELS(n) THEN "SUBCLASSOF" WHEN "LeadershipBehaviour" IN LABELS(n) THEN "CONSTITUTES" WHEN "Risk" IN LABELS(n) THEN "OFRISKAREA" WHEN "UPLCPhase" IN LABELS(n) THEN "PHASEOF" END AS nreltype WITH n, relatedNode, mainTitle, nreltype  MATCH (n)-[nty]->(parentN) WHERE TYPE(nty) CONTAINS nreltype WITH n, parentN, relatedNode, mainTitle, CASE WHEN "CoreFlow" IN LABELS(parentN) THEN parentN.title WHEN "LeadershipTopic" IN LABELS(parentN) THEN parentN.title WHEN "LeadershipTeamInteractionArea" IN LABELS(parentN) THEN parentN.name WHEN "RiskArea" IN LABELS(parentN) THEN parentN.name WHEN "LeadershipBehaviour" IN LABELS(parentN) THEN parentN.title WHEN "Risk" IN LABELS(parentN) THEN parentN.title WHEN "UPLifeCycle" IN LABELS(parentN) THEN parentN.name END AS parentname WITH n, parentname, relatedNode, mainTitle, CASE WHEN "Flow" IN LABELS(n) THEN "solarbird.flow" WHEN "CoreFlow" IN LABELS(n) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(n) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(n) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(n) THEN "solarbird.upphase" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + mainTitle, parent: parentname, connections: collect(relatedNode)}').data()
    seconddict = g.run('MATCH (n)-[first]->(k:Keyword)-[second]->(p) WHERE NOT n:Keyword AND NOT p:Keyword  WITH n,first,k,second,p, CASE WHEN first.rakeScore is null THEN 0.0 ELSE first.rakeScore END AS firstRakeScore WITH n,first,k,second,p,firstRakeScore, CASE WHEN second.rakeScore is null THEN 0.0 ELSE second.rakeScore END AS secondRakeScore WITH n, p, k, collect({keyword: k.name, weight: firstRakeScore +  secondRakeScore}) as keyRels WITH n, p, keyRels, reduce(totalWeight = 0, x IN keyRels| totalWeight + x.weight) AS completeWeight WITH n, p, keyRels, completeWeight, extract(item IN keyRels|item.keyword) AS kkeywords WITH n, p, keyRels, completeWeight, kkeywords, CASE  WHEN "Flow" IN LABELS(p) THEN p.title  WHEN "CoreFlow" IN LABELS(p) THEN p.title WHEN "LeadershipBehaviour" IN LABELS(p) THEN p.title WHEN "Risk" IN LABELS(p) THEN p.title WHEN "UPLCPhase" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, keyRels, completeWeight, connectedTitle, kkeywords, CASE WHEN "Flow" IN LABELS(p) THEN "PARTOFCOREFLOW"  WHEN "CoreFlow" IN LABELS(p) THEN "SUBCLASSOF" WHEN "LeadershipBehaviour" IN LABELS(p) THEN "CONSTITUTES" WHEN "Risk" IN LABELS(p) THEN "OFRISKAREA" WHEN "UPLCPhase" IN LABELS(p) THEN "PHASEOF" END AS preltype WITH n, p, keyRels, completeWeight, connectedTitle, kkeywords, preltype  MATCH (p)-[pt]->(parentNode) WHERE TYPE(pt) CONTAINS preltype WITH n, p, parentNode, keyRels, completeWeight, connectedTitle, kkeywords, CASE WHEN "CoreFlow" IN LABELS(parentNode) THEN parentNode.title WHEN "LeadershipTopic" IN LABELS(parentNode) THEN parentNode.title WHEN "LeadershipTeamInteractionArea" IN LABELS(parentNode) THEN parentNode.name WHEN "RiskArea" IN LABELS(parentNode) THEN parentNode.name WHEN "LeadershipBehaviour" IN LABELS(parentNode) THEN parentNode.title WHEN "Risk" IN LABELS(parentNode) THEN parentNode.title WHEN "UPLifeCycle" IN LABELS(parentNode) THEN parentNode.name END AS pparent WITH n, p, pparent, keyRels, completeWeight, connectedTitle, kkeywords, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(p) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(p) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(p) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(p) THEN "solarbird.upphase" END AS connectedTitleExtension WITH n, {name: connectedTitleExtension + "." + pparent + "." + connectedTitle, parent: pparent, weight: completeWeight, keywords: kkeywords,  semanticConnections: keyRels} as relatedNode  WITH n, relatedNode, CASE  WHEN "Flow" IN LABELS(n) THEN n.title  WHEN "CoreFlow" IN LABELS(n) THEN n.title WHEN "LeadershipBehaviour" IN LABELS(n) THEN n.title WHEN "Risk" IN LABELS(n) THEN n.title WHEN "UPLCPhase" IN LABELS(n) THEN n.name END AS mainTitle WITH n, relatedNode, mainTitle, CASE WHEN "Flow" IN LABELS(n) THEN "PARTOFCOREFLOW"  WHEN "CoreFlow" IN LABELS(n) THEN "SUBCLASSOF" WHEN "LeadershipBehaviour" IN LABELS(n) THEN "CONSTITUTES" WHEN "Risk" IN LABELS(n) THEN "OFRISKAREA" WHEN "UPLCPhase" IN LABELS(n) THEN "PHASEOF" END AS nreltype WITH n, relatedNode, mainTitle, nreltype  MATCH (n)-[nty]->(parentN) WHERE TYPE(nty) CONTAINS nreltype WITH n, parentN, relatedNode, mainTitle, CASE WHEN "CoreFlow" IN LABELS(parentN) THEN parentN.title WHEN "LeadershipTopic" IN LABELS(parentN) THEN parentN.title WHEN "LeadershipTeamInteractionArea" IN LABELS(parentN) THEN parentN.name WHEN "RiskArea" IN LABELS(parentN) THEN parentN.name WHEN "LeadershipBehaviour" IN LABELS(parentN) THEN parentN.title WHEN "Risk" IN LABELS(parentN) THEN parentN.title WHEN "UPLifeCycle" IN LABELS(parentN) THEN parentN.name END AS parentname WITH n, parentname, relatedNode, mainTitle, CASE WHEN "Flow" IN LABELS(n) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(n) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(n) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(n) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(n) THEN "solarbird.upphase" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + mainTitle, parent: parentname, connections: collect(relatedNode)}').data()
    thirddict = g.run('MATCH (n)-[first]->(p) WHERE NOT n:Keyword AND NOT p:Keyword  AND NOT n:RiskArea AND NOT p:RiskArea AND NOT n:TeamLeadershipRisk AND NOT p:TeamLeadershipRisk AND NOT n:LeadershipTeamInteractionArea AND NOT p:LeadershipTeamInteractionArea AND NOT n:LeadershipTeamInteraction AND NOT p:LeadershipTeamInteraction AND NOT n:UPLifeCycle AND NOT p:UPLifeCycle AND NOT n:LeadershipTopic AND NOT p:LeadershipTopic AND NOT n:EmotionBase AND NOT p:EmotionBase WITH n, p, first, CASE WHEN type(first)="SURFACESIN" THEN first.weight * 5 ELSE 80.0 END as theweight WITH n, p, first, theweight, CASE  WHEN "Flow" IN LABELS(p) THEN p.title  WHEN "CoreFlow" IN LABELS(p) THEN p.title WHEN "LeadershipBehaviour" IN LABELS(p) THEN p.title WHEN "Risk" IN LABELS(p) THEN p.title WHEN "UPLCPhase" IN LABELS(p) THEN p.name  WHEN "Emotion" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, first, theweight, connectedTitle, CASE WHEN "Flow" IN LABELS(p) THEN "PARTOFCOREFLOW"  WHEN "CoreFlow" IN LABELS(p) THEN "SUBCLASSOF" WHEN "LeadershipBehaviour" IN LABELS(p) THEN "CONSTITUTES" WHEN "Risk" IN LABELS(p) THEN "OFRISKAREA" WHEN "UPLCPhase" IN LABELS(p) THEN "PHASEOF"  WHEN "Emotion" IN LABELS(p) THEN "SUBCLASSOF" END AS preltype WITH n, p, first, theweight, connectedTitle, preltype  MATCH (p)-[pt]->(parentNode) WHERE TYPE(pt) CONTAINS preltype WITH n, p, first, theweight, parentNode, connectedTitle, CASE WHEN "Flow" IN LABELS(parentNode) THEN parentNode.title WHEN "CoreFlow" IN LABELS(parentNode) THEN parentNode.title WHEN "LeadershipTopic" IN LABELS(parentNode) THEN parentNode.title WHEN "LeadershipTeamInteractionArea" IN LABELS(parentNode) THEN parentNode.name WHEN "RiskArea" IN LABELS(parentNode) THEN parentNode.name WHEN "LeadershipBehaviour" IN LABELS(parentNode) THEN parentNode.title WHEN "Risk" IN LABELS(parentNode) THEN parentNode.title WHEN "UPLifeCycle" IN LABELS(parentNode) THEN parentNode.name  WHEN "EmotionBase" IN LABELS(parentNode) THEN parentNode.name END AS pparent WITH n, p, first, theweight, connectedTitle, pparent, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(p) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(p) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(p) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(p) THEN "solarbird.upphase"  WHEN "Emotion" IN LABELS(p) THEN "solarbird.emotion" END AS connectedTitleExtension WITH n, p, theweight, pparent, connectedTitle, connectedTitleExtension, collect({relType: type(first)}) as keyRels WITH n, {name: connectedTitleExtension + "." + pparent + "." + connectedTitle, parent: pparent, weight: theweight, keywords: [],  semanticConnections: keyRels} as relatedNode  WITH n, relatedNode, CASE  WHEN "Flow" IN LABELS(n) THEN n.title  WHEN "CoreFlow" IN LABELS(n) THEN n.title WHEN "LeadershipBehaviour" IN LABELS(n) THEN n.title WHEN "Risk" IN LABELS(n) THEN n.title WHEN "UPLCPhase" IN LABELS(n) THEN n.name  WHEN "Emotion" IN LABELS(n) THEN n.name END AS mainTitle WITH n, relatedNode, mainTitle, CASE WHEN "Flow" IN LABELS(n) THEN "PARTOFCOREFLOW"  WHEN "CoreFlow" IN LABELS(n) THEN "SUBCLASSOF" WHEN "LeadershipBehaviour" IN LABELS(n) THEN "CONSTITUTES" WHEN "Risk" IN LABELS(n) THEN "OFRISKAREA" WHEN "UPLCPhase" IN LABELS(n) THEN "PHASEOF"  WHEN "Emotion" IN LABELS(n) THEN "SUBCLASSOF" END AS nreltype WITH n, relatedNode, mainTitle, nreltype  MATCH (n)-[nty]->(parentN) WHERE TYPE(nty) CONTAINS nreltype WITH n, parentN, relatedNode, mainTitle, CASE WHEN "CoreFlow" IN LABELS(parentN) THEN parentN.title WHEN "LeadershipTopic" IN LABELS(parentN) THEN parentN.title WHEN "LeadershipTeamInteractionArea" IN LABELS(parentN) THEN parentN.name WHEN "RiskArea" IN LABELS(parentN) THEN parentN.name WHEN "LeadershipBehaviour" IN LABELS(parentN) THEN parentN.title WHEN "Risk" IN LABELS(parentN) THEN parentN.title WHEN "UPLifeCycle" IN LABELS(parentN) THEN parentN.name  WHEN "EmotionBase" IN LABELS(parentN) THEN parentN.name END AS parentname WITH n, parentname, relatedNode, mainTitle, CASE WHEN "Flow" IN LABELS(n) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(n) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(n) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(n) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(n) THEN "solarbird.upphase"  WHEN "Emotion" IN LABELS(n) THEN "solarbird.emotion" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + mainTitle, parent: parentname, connections: collect(relatedNode)}').data()


    myfuturejson = []
    tobemergedA = []
    tobemergedB = []

    for iteratingitem in firstdict:
        item = iteratingitem["n"]
        nicefirstdict = {}
        nicefirstdict['name'] = item['name']
        newconnections = []
        if item["connections"]:
           myconnections = item["connections"]
           for conn in myconnections:
               keywords = []
               relationshiptypes = []
               if conn["keywords"]:
                   keywords = list(set(conn["keywords"]))
               if conn["relationshipTypes"]:
                   relationshiptypes = list(set(conn["relationshipTypes"]))
               newconnection = {"name":conn["name"], "weight":conn["weight"], "keywords":keywords, "relationshiptypes":relationshiptypes, "semanticrelationships":conn["semanticConnections"]}
               newconnections.append(newconnection)
        nicefirstdict["connections"] = newconnections
        myfuturejson.append(nicefirstdict)
  
    for iteratingitem in seconddict:
        item = iteratingitem["n"]
        niceseconddict = {}
        niceseconddict['name'] = item['name']
        newconnections = []
        if item["connections"]:
           myconnections = item["connections"]
           for conn in myconnections:
               keywords = []
               relationshiptypes = []
               if conn["keywords"]:
                   keywords = list(set(conn["keywords"]))
               newconnection = {"name":conn["name"], "weight":conn["weight"], "keywords":keywords, "relationshiptypes":relationshiptypes}
               newconnections.append(newconnection)
        niceseconddict["connections"] = newconnections
        tobemergedA.append(niceseconddict)
    
    for iteratingitem in thirddict:
        item = iteratingitem["n"]
        nicethirddict = {}
        nicethirddict['name'] = item['name']
        newconnections = []
        if item["connections"]:
           myconnections = item["connections"]
           for conn in myconnections:
               keywords = []
               relationshiptypes = []
               if conn["semanticConnections"]:
                   myreltypes = []
                   semRels = conn["semanticConnections"]
                   for i in semRels:
                       myreltypes.append(i["relType"])
                   relationshiptypes = list(set(myreltypes))
               newconnection = {"name":conn["name"], "weight":conn["weight"], "keywords":keywords, "relationshiptypes":relationshiptypes}
               newconnections.append(newconnection)
        nicethirddict["connections"] = newconnections
        tobemergedB.append(nicethirddict)

    #print len(tobemergedB) 
    ru = list_enhance(myfuturejson)  
    ma = list_enhance(tobemergedA) 
    mu = list_enhance(tobemergedB)  
 

    mynewjson = list_merge(ru, ma)
    anotherjson = list_merge(mynewjson, mu)
    finaljson = list_enhance(anotherjson)

    namearray = []
    for item in finaljson:
        namearray.append(item["name"])
    namearray = list(set(namearray))
    mergearray = []
    for item in tobemergedB:
        mergearray.append(item["name"])
    mergearray = list(set(mergearray))
    nameset = set(mergearray) - set(namearray)
    thenames = list(nameset)
    print("*******")
    print(thenames)
    print("*******") 
    #print len(namearray)            
    #print len(finaljson)
    with open('result.json', 'w') as fp:
        json.dump(finaljson, fp)
    return(json.dumps(finaljson))

def getflowdata(name):
    flowjson = g.run('MATCH (n:Flow)-[first]->(p) WHERE n.title="' + name + '" AND NOT p:RiskArea AND NOT p:TeamLeadershipRisk AND NOT p:LeadershipTeamInteractionArea AND NOT p:LeadershipTeamInteraction AND NOT p:UPLifeCycle AND NOT p:LeadershipTopic AND NOT p:EmotionBase WITH n, p, first, CASE  WHEN "CoreFlow" IN LABELS(p) THEN p.title WHEN "LeadershipBehaviour" IN LABELS(p) THEN p.title WHEN "Risk" IN LABELS(p) THEN p.title WHEN "UPLCPhase" IN LABELS(p) THEN p.name  WHEN "Keyword" IN LABELS(p) THEN p.name WHEN "Emotion" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, first, connectedTitle, CASE WHEN type(first)="RELATEDTOKEYWORD" THEN first.rakeScore ELSE 0.0 END AS weight WITH n, p, first, weight, connectedTitle, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(p) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(p) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(p) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(p) THEN "solarbird.upphase"  WHEN "Emotion" IN LABELS(p) THEN "solarbird.emotion"  WHEN "Keyword" IN LABELS(p) THEN "solarbird.keyword" END AS connectedTitleExtension  WITH n, {name: connectedTitleExtension + "." + connectedTitle, weight: weight} as relatedNode MATCH (n)-[nty:PARTOFCOREFLOW]->(parentN)  WITH n, parentN, relatedNode, CASE WHEN "CoreFlow" IN LABELS(parentN) THEN parentN.title END AS parentname WITH n, parentname, relatedNode, CASE WHEN "Flow" IN LABELS(n) THEN "solarbird.flow"   WHEN "CoreFlow" IN LABELS(n) THEN "solarbird.coreflow"  WHEN "LeadershipBehaviour" IN LABELS(n) THEN "solarbird.behaviour"  WHEN "Risk" IN LABELS(n) THEN "solarbird.risk"  WHEN "UPLCPhase" IN LABELS(n) THEN "solarbird.upphase"  WHEN "Emotion" IN LABELS(n) THEN "solarbird.emotion" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + n.title, parent: parentname, pictureURL: n.pictureURL, referenceURL: n.referenceURL, sentiment: n.sentiment, description: n.description, connections: collect(relatedNode)}').data()
    return(json.dumps(flowjson))
    

def getupdata(name):
    upjson = g.run('MATCH (n:UPLCPhase)-[first]->(p) WHERE n.name="' + name + '" AND NOT p:RiskArea AND NOT p:TeamLeadershipRisk AND NOT p:LeadershipTeamInteractionArea AND NOT p:LeadershipTeamInteraction AND NOT p:UPLifeCycle AND NOT p:LeadershipTopic AND NOT p:EmotionBase AND NOT p:UPLCPhase WITH n, p, first, CASE  WHEN "Flow" IN LABELS(p) THEN p.title WHEN "Keyword" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, first, connectedTitle, CASE WHEN type(first)="RELATEDTOKEYWORD" THEN first.rakeScore WHEN "Flow" IN LABELS(p) THEN p.centrality ELSE 0.0 END AS weight WITH n, p, first, weight, connectedTitle, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow" WHEN "Keyword" IN LABELS(p) THEN "solarbird.keyword" END AS connectedTitleExtension  WITH n, {name: connectedTitleExtension + "." + connectedTitle, weight: weight} as relatedNode MATCH (n)-[nty:PHASEOF]->(parentN)  WITH n, parentN, relatedNode, CASE WHEN "UPLifeCycle" IN LABELS(parentN) THEN parentN.name END AS parentname WITH n, parentname, relatedNode, CASE WHEN "UPLCPhase" IN LABELS(n) THEN "solarbird.upphase" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + n.name, parent: parentname, description: n.description, pictureURL: n.pictureURL, referenceURL: n.referenceURL, connections: collect(relatedNode)}').data()
    return(json.dumps(upjson))

def getbehaviourdata(name):
    datastring = ""
    if name == "Managing Team Boundaries":
        datastring = 'MATCH (n:LeadershipBehaviour) WHERE n.title="Managing Team Boundaries" RETURN n {name: "solarbird.behaviour." + n.title, referenceURL: n.referenceURL}'
    elif name == "Systems Sensing":
        datastring = 'MATCH (n:LeadershipBehaviour) WHERE n.title="Systems Sensing" RETURN n {name: "solarbird.behaviour." + n.title, referenceURL: n.referenceURL}'
    else:
        datastring = 'MATCH (n:LeadershipBehaviour)-[first]->(p) WHERE n.title="' + name + '" AND NOT p:LeadershipBehaviour AND NOT p:LeadershipTeamInteractionArea WITH n, p, first, CASE  WHEN "Flow" IN LABELS(p) THEN p.title WHEN "Keyword" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, first, connectedTitle, CASE WHEN type(first)="HASHEURISTICS" THEN 50.0 WHEN "Flow" IN LABELS(p) THEN p.centrality ELSE 0.0 END AS weight WITH n, p, first, weight, connectedTitle, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow" WHEN "Keyword" IN LABELS(p) THEN "solarbird.keyword" END AS connectedTitleExtension  WITH n, {name: connectedTitleExtension + "." + connectedTitle, weight: weight} as relatedNode MATCH (n)-[nty:CONSTITUTES]->(parentN)  WITH n, parentN, relatedNode, CASE WHEN "LeadershipTeamInteractionArea" IN LABELS(parentN) THEN parentN.name WHEN "LeadershipBehaviour" IN LABELS(parentN) THEN parentN.title END AS parentname WITH n, parentname, relatedNode, CASE WHEN "LeadershipBehaviour" IN LABELS(n) THEN "solarbird.behaviour" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + n.title, parent: parentname, description: n.heuristics, referenceURL: n.referenceURL, connections: collect(relatedNode)}'
    behaviourjson = g.run(datastring).data()
    print(behaviourjson)
    return(json.dumps(behaviourjson))


def getriskdata(name):
    datastring = ""
    if name == "Interdependence and Trust":
        datastring = 'MATCH (n:Risk) WHERE n.title="Interdependence and Trust" RETURN n {name: "solarbird.risk." + n.title, referenceURL: n.referenceURL}'
    else:
        datastring = 'MATCH (n:Risk)-[first]->(p) WHERE n.title="' + name + '" AND NOT p:Risk AND NOT p:RiskArea WITH n, p, first, CASE  WHEN "Flow" IN LABELS(p) THEN p.title WHEN "Keyword" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, first, connectedTitle, CASE WHEN type(first)="HASHEURISTICS" THEN 50.0 WHEN "Flow" IN LABELS(p) THEN p.centrality ELSE 0.0 END AS weight WITH n, p, first, weight, connectedTitle, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow" WHEN "Keyword" IN LABELS(p) THEN "solarbird.keyword" END AS connectedTitleExtension  WITH n, {name: connectedTitleExtension + "." + connectedTitle, weight: weight} as relatedNode MATCH (n)-[nty:OFRISKAREA]->(parentN)  WITH n, parentN, relatedNode, CASE WHEN "RiskArea" IN LABELS(parentN) THEN parentN.name WHEN "Risk" IN LABELS(parentN) THEN parentN.title END AS parentname WITH n, parentname, relatedNode, CASE WHEN "Risk" IN LABELS(n) THEN "solarbird.risk" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + n.title, parent: parentname, description: n.heuristics, referenceURL: n.referenceURL, connections: collect(relatedNode)}'
    behaviourjson = g.run(datastring).data()
    print(behaviourjson)
    return(json.dumps(behaviourjson))


def getcfdata(name):
    upjson = g.run('MATCH (n:CoreFlow)-[first]->(p) WHERE n.title="' + name + '" AND NOT p:LeadershipTopic AND NOT p:RiskArea AND NOT p:TeamLeadershipRisk AND NOT p:LeadershipTeamInteractionArea AND NOT p:LeadershipTeamInteraction AND NOT p:UPLifeCycle AND NOT p:LeadershipTopic AND NOT p:EmotionBase AND NOT p:UPLCPhase WITH n, p, first, CASE  WHEN "Flow" IN LABELS(p) THEN p.title WHEN "Keyword" IN LABELS(p) THEN p.name END AS connectedTitle WITH n, p, first, connectedTitle, CASE WHEN type(first)="RELATEDTOKEYWORD" THEN first.rakeScore WHEN "Flow" IN LABELS(p) THEN p.centrality ELSE 0.0 END AS weight WITH n, p, first, weight, connectedTitle, CASE  WHEN "Flow" IN LABELS(p) THEN "solarbird.flow" WHEN "Keyword" IN LABELS(p) THEN "solarbird.keyword" END AS connectedTitleExtension  WITH n, {name: connectedTitleExtension + "." + connectedTitle, weight: weight} as relatedNode MATCH (n)-[nty:SUBCLASSOF]->(parentN)  WITH n, parentN, relatedNode, CASE WHEN "LeadershipTopic" IN LABELS(parentN) THEN parentN.title END AS parentname WITH n, parentname, relatedNode, CASE WHEN "CoreFlow" IN LABELS(n) THEN "solarbird.coreflow" END AS mainTitleExtension RETURN n {name: mainTitleExtension + "." + parentname + "." + n.title, parent: parentname, description: n.description, pictureURL: n.pictureURL, connections: collect(relatedNode)}').data() 
    return(json.dumps(upjson))

def getemotiondata(name):
    emotionjson = g.run('MATCH (n:Emotion) WHERE n.name="' + name + '" RETURN n {name: "solarbird.emotion." + n.name, referenceURL: n.referenceURL}').data()
    return(json.dumps(emotionjson))

getontologydata()
