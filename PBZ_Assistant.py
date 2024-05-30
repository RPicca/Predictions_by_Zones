import win32com.client
import os

def Get_Selection():
    doc=Atoll.ActiveDocument
    return win32com.client.dynamic.Dispatch(doc.Selection)   

def AtollMacro_Prediction_Info():
    elmt=win32com.client.dynamic.Dispatch(Get_Selection())
    print(elmt.Name)
    print("Par émétteur : " + str(elmt.ISPERTRANSMITTER))

#Lancement depuis une prédiction
def AtollMacro_Set_Computation_to_prediction_zone():
    doc=Atoll.ActiveDocument
    pred=win32com.client.dynamic.Dispatch(Get_Selection())
    X_pred = pred.USERDATA.Get("Forsk.PredictionsByZones").Get("xcoordinates")
    Y_pred= pred.USERDATA.Get("Forsk.PredictionsByZones").Get("ycoordinates")
    #On assemble les coord X avec les Y
    Pts=[]
    #Pour gérer les cas où il y a plusieurs poly
    for p in range(len(X_pred)):
        poly=[]
        #On évite le premier élément qui est un bool
        for c in range(1,len(X_pred[p])):
            poly.append((X_pred[p][c],Y_pred[p][c]))
        Pts.append(poly)
    Pts=Pts
    zones=win32com.client.dynamic.Dispatch(doc.GetRecords("Zones", True))
    #On supprime l'ancienne zone de calcul
    iRow=0
    while iRow != -1:
        iRow = zones.Find(0, "NAME", 0, "ComputationZone")
        if iRow != -1:
            zones.Delete(iRow)
    #Pour chaque polygone, on ajoute une ligne à la table des zones
    for poly in range(len(Pts)):
        zones.AddNew()
        zones.SetValue("NAME", "ComputationZone")
        zones.SetValue("CONTOUR_NUM", poly)
        zones.SetValue("POLYGON_NUM", 0)
        zones.SetValue("POINTS", Pts[poly])
        zones.Update()


def AtollMacro_Set_Computation_to_predictions_zones():
    Set_Zone_to_predictions_zones("ComputationZone")

def AtollMacro_Set_Focus_to_predictions_zones():
    Set_Zone_to_predictions_zones("FocusZone")


#TODO : éviter le copier coller
#Lancement depuis un dossier
def Set_Zone_to_predictions_zones(Zone):
    doc=Atoll.ActiveDocument
    #On supprime l'ancienne zone de calcul
    iRow=0
    zones=win32com.client.dynamic.Dispatch(doc.GetRecords("Zones", True))
    while iRow != -1:
        iRow = zones.Find(0, "NAME", 0, Zone)
        if iRow != -1:
            zones.Delete(iRow)
    folder=win32com.client.dynamic.Dispatch(Get_Selection())
    #On boucle sur les pred du dossier
    for pred in folder:
        X_pred = pred.USERDATA.Get("Forsk.PredictionsByZones").Get("xcoordinates")
        Y_pred = pred.USERDATA.Get("Forsk.PredictionsByZones").Get("ycoordinates")
        #On assemble les coord X avec les Y
        Pts=[]
        #Pour gérer les cas où il y a plusieurs poly
        for p in range(len(X_pred)):
            poly=[]
            #On évite le premier élément qui est un bool
            for c in range(1,len(X_pred[p])):
                poly.append((X_pred[p][c],Y_pred[p][c]))
            Pts.append(poly)
        #Pour chaque polygone, on ajoute une ligne à la table des zones
        for poly in range(len(Pts)):
            zones.AddNew()
            zones.SetValue("NAME", Zone)
            zones.SetValue("CONTOUR_NUM", poly)
            zones.SetValue("POLYGON_NUM", 0)
            zones.SetValue("POINTS", Pts[poly])
            zones.Update()
#Lancement depuis un dossier de run            
def AtollMacro_Report():
    doc=Atoll.ActiveDocument
    report_path=os.path.join(doc.Path,"PBZ_"+str(doc.Name))
    if not os.path.exists(report_path):
        os.mkdir(report_path)
    pbz = doc.GetService("{2ACFBDB0-A92D-42B3-ACE6-EE719A713FF4}")
    pbz.SetDocument(doc)
    #On boucle sur tous les dossiers du run sélectionné et on génère un report dessus
    folder = Get_Selection()
    for f in folder._NewEnum():
        file_name=f.Name.replace("/", "_").replace(":", "-")+".txt"
        file_path=os.path.join(report_path,file_name)
        print(file_path)
        try:
            pbz.report(f, ["Surface (km²)", "% of Covered Area", "% Focus Zone", "% Computation Zone"], "\t", file_path)
        except:
            f = open(file_path+"_EMPTY", "w")
            f.close()

    
def AtollMacro_Print_CPZ():
    doc=Atoll.ActiveDocument
    zones=win32com.client.dynamic.Dispatch(doc.GetRecords("Zones", True))
    # On a une ligne par polygone dans la CPZ, on les affiche tous
    iRow=0
    while iRow != -1:
        iRow = zones.Find(iRow+1, "NAME", 0, "ComputationZone")
        if iRow!=-1:
            print(zones.GetValue(iRow, "POINTS"))

def AtollMacro_Selection_Name():
    print(Get_Selection().Name)




