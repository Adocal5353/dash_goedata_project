import geopandas as gpd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import json
import pandas as pd
from utils.functions import get_data_month, get_geo_json_data,set_indice_proprete


#Charger les données des maisons
maison_data = get_data_month("maisons_datas.csv")


# Charger le fichier GeoJSON
geo_data = get_geo_json_data("geojsons/lomé.geo.json")
geo_data = set_indice_proprete(maison_data,geo_data)


# Filtrer les délimitations des administrations
gdf_administrations = geo_data[geo_data['tags'].apply(lambda x: x.get('admin_level', None)) == '9']

# Créer la première carte Plotly Express avec les grandes subdivisions
fig = px.choropleth_mapbox(gdf_administrations, 
                            geojson=gdf_administrations.geometry, 
                            locations=gdf_administrations.index, 
                            color='indice_proprete',
                            color_continuous_scale="RdYlGn",  # Échelle de couleur du rouge au vert
                            mapbox_style="carto-positron",
                            hover_name='name',
                            range_color=(1, 10),  # Spécifier les valeurs minimales et maximales de l'échelle de couleur
                            zoom=11, 
                            center={"lat": gdf_administrations.geometry.centroid.y.mean(), "lon": gdf_administrations.geometry.centroid.x.mean()},
                            opacity=0.5,
                            labels={'indice_proprete':'Indice de propreté'}
                        )
fig.update_layout(title_text="Carte de l'indice de propreté des administrations")

# Créer l'application Dash
app = dash.Dash(__name__)

#céation du serveur 
server=app.server

# Définir la mise en page de l'application Dash
app.layout = html.Div([
    html.H1(children='Carte des indices de propreté(Cas de la ville de Lomé)', style={'textAlign':'center'}),
    dcc.Dropdown(options=[
        {"label":"Tous" , "value":""},
        {"label":"Janvier" , "value":"JANV"},
        {"label":"Fevrier" , "value":"FEV"},
        {"label":"Mars" , "value":"MARS"},
        {"label":"Avril" , "value":"AVRIL"},
        {"label":"Mai" , "value":"MAI"},
        {"label":"Juin" , "value":"JUIN"},
        {"label":"Juillet" , "value":"JUIL"},
        {"label":"Août" , "value":"AOUT"},
        {"label":"Septembre" , "value":"SEPT"},
        {"label":"Octobre" , "value":"OCT"},
        {"label":"Novembre" , "value":"NOV"},
        {"label":"Decembre" , "value":"DEC"},
        ],
        value="",
        id='dropdown-selection'),
    dcc.Graph(figure=fig, id='map-click'),
    html.Div(id='map-subdivisions')
])

# définir la fonction de callback qui met à jour la carte en fonction du mois 
@app.callback(
    Output(component_id='map-click',component_property='figure'),
    Input('dropdown-selection','value'),
    prevent_initial_call=True
)
def update_arrond_map(value):
    maison_data= get_data_month("maisons_datas.csv",value)
    geo_data = get_geo_json_data("geojsons/lomé.geo.json")
    geo_data = set_indice_proprete(maison_data,geo_data)
    
    # Filtrer les délimitations des administrations
    gdf_administrations = geo_data[geo_data['tags'].apply(lambda x: x.get('admin_level', None)) == '9']

    # Créer la première carte Plotly Express avec les grandes subdivisions
    fig = px.choropleth_mapbox(gdf_administrations, 
                            geojson=gdf_administrations.geometry, 
                            locations=gdf_administrations.index, 
                            color='indice_proprete',
                            color_continuous_scale="RdYlGn",  # Échelle de couleur du rouge au vert
                            mapbox_style="carto-positron",
                            hover_name='name',
                            range_color=(1, 10),  # Spécifier les valeurs minimales et maximales de l'échelle de couleur
                            zoom=11, 
                            center={"lat": gdf_administrations.geometry.centroid.y.mean(), "lon": gdf_administrations.geometry.centroid.x.mean()},
                            opacity=0.5,
                            labels={'indice_proprete':'Indice de propreté'}
                        )
    fig.update_layout(transition_duration=500,title_text="Carte de l'indice de propreté des arrondissements de Lomé")
    return fig


# Définir la fonction callback pour afficher les sous-divisions au clic
@app.callback(
    Output('map-subdivisions','children'),
    [Input('map-click', 'clickData')],
    Input('dropdown-selection','value')

)
def display_subdivisions(clickData,value):
    if clickData is not None:
        maison_data= get_data_month("maisons_datas.csv",value)
        geo_data = get_geo_json_data("geojsons/lomé.geo.json")
        geo_data = set_indice_proprete(maison_data,geo_data)
    
        index = clickData['points'][0]['location']
        subdivision_id = geo_data.loc[index, 'id']
        print(clickData['points'][0]['location'])
        
        # Filtrer les sous-divisions de la grande subdivision sélectionnée
        gdf_quartiers = geo_data[geo_data['relations'].apply(lambda x: json.loads(x)[0]['rel'] == subdivision_id)]
        
        # Créer la deuxième carte Plotly Express avec les sous-divisions
        fig_quartiers = px.choropleth_mapbox(gdf_quartiers, 
                            geojson=gdf_quartiers.geometry, 
                            locations=gdf_quartiers.index, 
                            color='indice_proprete',
                            color_continuous_scale="RdYlGn",  # Échelle de couleur du rouge au vert
                            mapbox_style="carto-positron",
                            hover_name='name',
                            range_color=(1, 10),  # Spécifier les valeurs minimales et maximales de l'échelle de couleur
                            zoom=11.8, 
                            center={"lat": gdf_quartiers.geometry.centroid.y.mean(), "lon": gdf_quartiers.geometry.centroid.x.mean()},
                            opacity=0.5,
                            labels={'indice_proprete':'Indice de propreté'}
                        )
        fig_quartiers.update_layout(title_text="Carte de l'indice de propreté du "+geo_data.loc[index, 'name'])
        return dcc.Graph(figure=fig_quartiers)

# Exécuter l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)
