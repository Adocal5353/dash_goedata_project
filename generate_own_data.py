# this file will help us generate our own data.

import json
import random
from datetime import datetime, timedelta
import geopandas as gpd
import csv


class Arrondissement:
    def __init__(self,id:int,nom:str) -> None:
        self.id = id
        self.nom = nom
    def jsonify(self):
        return {
            "id":self.id,
            "name":self.nom
        }
    


class Quartier:
    def __init__(self,id:int,nom:str,arrondissement:Arrondissement) -> None:
        self.id = id
        self.nom = nom
        self.arrondissement = arrondissement
        
    def jsonify(self):
        return{
            "id" : self.id,
            "nom":  self.nom,
            "arrondissement": self.arrondissement.jsonify() if isinstance(self.arrondissement, Arrondissement) else self.arrondissement
        }



class Maison:
    def __init__(self, id:int,quartier:Quartier):
        self.id = id
        self.quartier = quartier
        self.note_agence = round(random.uniform(0, 10), 2)  # Note donnée par la compagnie de ramassage
        self.note_maison = round(random.uniform(0, 10), 2)  # Note attribuée à la maison
        self.mois = random.choice(["JANV","FEV","MARS","AVRIL","MAI","JUIN","JUIL","AOUT","SEPT","OCT","NOV","DEC"])

    def jsonify(self):
        return {
            "id": self.id,
            "note_agence": self.note_agence,
            "note_maison": self.note_maison
        }
    
    def to_list(self):
        return  [self.id, self.quartier.arrondissement.id, self.quartier.id, self.note_agence,self.note_maison,self.mois]


        
def _extract_quartiers():
    chemin_fichier_json = "separations_quartiers/data/lomé.geo.json"

    gdf = gpd.read_file(chemin_fichier_json)
    gdf_arrondissement = gdf[gdf['tags'].apply(lambda x: x.get('admin_level', None)) == '10']

    quartiers = []
    for index, row in gdf_arrondissement.iterrows():
        quartiers.append(Quartier(id=row["id"],nom=row["tags"]["name"],arrondissement=Arrondissement(id=json.loads(row["relations"])[0]["rel"],nom=json.loads(row["relations"])[0]["reltags"]["name"])))
        
    return quartiers


def _generate_maisons(nombre):
    quartiers = _extract_quartiers()
    lenght =  len(quartiers)
    maisons:list[Maison]=[]
    for i in quartiers:
        maisons.extend([Maison(id=k,quartier=i) for k in range(1,nombre+1)])
        
    list_maisons = [maison.to_list() for maison in maisons]

    return list_maisons


def generate_data(filename:str):
    maisons_data = [["id","arrondissement_id","quartier_id","note_maison","note_agence","mois"]]
    
    maisons_data.extend(_generate_maisons(50))

    with open(filename, 'w', newline='') as fichier_csv:
            writer = csv.writer(fichier_csv,delimiter=';')
            writer.writerows(maisons_data)
            

if __name__=='__main__':
    generate_data("maisons_datas.csv")