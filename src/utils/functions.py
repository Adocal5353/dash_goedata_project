import pandas as pd
import geopandas as gpd
import json

def get_data_month(filename,mois=""):
    all_month= ["JANV","FEV","MARS","AVRIL","MAI","JUIN","JUIL","AOUT","SEPT","OCT","NOV","DEC"]
    data = pd.read_csv(filename,delimiter=";")
    data["moyenne_maison"] =  (data["note_maison"] + data["note_agence"]) / 2
    if mois =="" or mois not in all_month:
        return data.copy()
    else:
        return data[data['mois'] ==mois].copy()



def get_geo_json_data(filename):
    gdf = gpd.read_file(filename)
    gdf['name'] = gdf['tags'].apply(lambda x: x['name'])
    return gdf.copy()


def set_indice_proprete(maison_data,geo_data):
    
    #on sélectionne uniquement les quartiers
    gdf_quartiers = geo_data[geo_data['tags'].apply(lambda x: x.get('admin_level', None)) == '10']


    gdf_quartiers = gdf_quartiers.merge(maison_data, left_on="id", right_on="quartier_id", how="left")


    # Calculer la moyenne de la colonne 'moy_maison'
    moyenne_moy_maison = gdf_quartiers[["id_x","moyenne_maison"]].groupby("id_x").mean().round(2)


    # Créer un dictionnaire avec les ID et les moyennes correspondantes
    moyenne_dict = moyenne_moy_maison['moyenne_maison'].to_dict()

    # Affecter les moyennes correspondantes à la colonne 'indice_proprete' de 'gdf'
    geo_data['indice_proprete'] = geo_data['id'].map(moyenne_dict)
    
    #Maintenant on calule les indices  de propreté des grande administrations
    
        
    partial_arrond_extracted = []


    # Parcourir chaque ligne du DataFrame gdf
    for index, row in geo_data.iterrows():
        # Vérifier si la valeur de la clé "admin_level" est égale à 10
        if 'tags' in row and row['tags'].get('admin_level') == '10':
            # Créer un dictionnaire pour stocker les données à extraire
            extract_info = {}
        
            # Extraire le rel
            extract_info['rel'] = json.loads(row['relations'])[0]['rel']
            
            # Extraire l'indice de propreté
            extract_info['indice_proprete'] = row['indice_proprete']
            
            # Ajouter les données extraites à la liste
            partial_arrond_extracted.append(extract_info)

    arrondissements = pd.DataFrame(partial_arrond_extracted)

    indice_arrondissement = arrondissements[["rel","indice_proprete"]].groupby("rel").mean().round(2)
    indice_arrondissement_dict= indice_arrondissement["indice_proprete"].to_dict()
    geo_data['indice_proprete'] = geo_data['id'].map(indice_arrondissement_dict).combine_first(geo_data['indice_proprete'])
    
    return geo_data.copy()
            