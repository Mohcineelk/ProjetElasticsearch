# ############################################################################################################ #
#                                 Programme : "OLAP"                                                           #
#                                                                                                              #
#                                 Dernière modification : 10/03/2021                                           #
#                                                                                                              #
#                                 Réalise par : EL KHADIMI Mohcine / SLIM Malik                                #
#                                                                                                              #                                                                                                              #
#                                                                                                              #
#                                                                                                              #
# ############################################################################################################ #

#librairies à importer

#Import Python GUI 
import tkinter 
from tkinter import *
from tkinter import ttk
# Import pivot table ui 
from pivottablejs import pivot_ui
# Import web libraries
from IPython.display import HTML
import webbrowser
# Import Elasticsearch package 
from elasticsearch import Elasticsearch 
import json
import requests
import pandas as pd
import io
import numpy as np

# Connexion au serveur d'elasticsearch
es=Elasticsearch([{'host':'localhost','port':9200}])

#configuration de l'interface graphique
root = Tk()
root.title("Sensor Data")
root.geometry("920x520")
root.minsize(480,360)
root.config(background='#4065A4')

#créer le frame principal 
main_frame = Frame(root,bg='#4065A4')
main_frame.pack(fill=BOTH, expand=1)

# Créer un widget Canvas 
my_canvas = Canvas(main_frame,bg='#4065A4')
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Ajout d'une Scrollbar au Canvas
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

# Configuration du Canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))


# Créer un second frame dans le canvas
second_frame = Frame(my_canvas,bg='#4065A4')

# Add that New frame To a Window In The Canvas
my_canvas.create_window((0,0), window=second_frame, anchor="center")

# créer des frames pour chaque partie de l'interface graphique 
dimension_frame = Frame(second_frame,bg='#4065A4')
geospatial_frame = Frame(second_frame,bg='#4065A4')
button_frame = Frame(second_frame,bg='#4065A4')


#######################################################################################################################
#- la fonction generate_geoquery renvoie un dictionnaire contenant la requête dsl pour effectuer le filtre géospatial #
#                                                                                                                     #
#######################################################################################################################

def generate_geoquery():
    query = {}

    #si l'utilisateur a saisi les coordonnées d'un seul point (ie: il veut calculer une distance)
    if (len(liste) == 1):
        #récupérer la distance saisie
        distance = enter_distance.get()
        #générer la requête dsl
        query = {
            "geo_distance": {
            "distance": distance,
                "Coord": liste[0]
            }
        }
    #sinon si l'utilisateur a saisi les coordonnées d'au moins 3 points (polygone)
    elif (len(liste) >= 3):
        #ajouter à la fin de la liste son premier élément pour avoir tous les points constituant le polygone (forme fermée
        # donc le premier point est lui même le dernier)
        liste.append(liste[0])
        #récupérer la relation choisie par l'utilisateur parmi celles proposées
        relation = choose_relation.get() 
        #générer la requête dsl
        query = {
            "geo_shape": {
                "ignore_unmapped": True,
                "Coord": {
                "relation": relation,
                "shape": {
                    "coordinates": [
                    liste  
                    ],
                    "type": "Polygon"
                }
                }
            }
        }
    return query

#####################################################################################################################
#                                                                                                                   #
#- la fonction joined_data prend comme paramètres la dimension temps ainsi que la (ou les) mesure(s)                #
#choisies par l'utilisateur sur l'interface graphique et crée le dataframe qui joint des données sensor et network  #
#                                                                                                                   #
#####################################################################################################################
def joined_data(my_dimension_temps,my_measure):
   
    geo_query = generate_geoquery()
    query_network={}

    #Si l'utilisateur n'a pas choisi de filtrer avec une requête géospatiale
    if (geo_query == {}):
        #générer la requête SQL qui récupère les ids des noeuds, leur type et leurs coordonnées à partir de l'index network
        query_network = json.dumps({"query":"SELECT myNodeId, nodeType, Coord FROM network",
                                "fetch_size":10000})
    #sinon, on génère la même requête SQL en la filtrant grâce à la requête géospatiale DSL
    else : 
        query_network= json.dumps({"query":"SELECT myNodeId, nodeType, Coord FROM network",
                                    "filter" : geo_query,
                                    "fetch_size":10000})

    #envoyer la requête au serveur d'elasticsearch et récupérer le résultat dans le dataframe df_network
    req_network = requests.post("http://localhost:9200/_sql", data=query_network, headers={'Content-Type':'application/json'})
    response_network = req_network.json()
    df_network = pd.DataFrame(response_network['rows'],
                    columns=[d['name'] for d in response_network['columns']])
    

    query_sensor=""
    #si l'utilisateur a choisi un niveau dans la dimension temps
    if (my_dimension_temps) :
        #générer la requête SQL qui récupère la dimension temps, la (ou les) mesure(s) et l'id des noeuds à partir de l'index sensor
        query_sensor=json.dumps({"query":"SELECT "+my_dimension_temps+",myNodeId, "+my_measure+ " FROM sensor ",
        "fetch_size": 10000})

    #sinon, la requête ne récupère que les ids des noeuds et la(ou les) mesure(s)
    else :
        query_sensor= json.dumps({"query":"SELECT myNodeId, "+my_measure+ " FROM sensor ",
        "fetch_size" : 10000})

    #envoyer la requête au serveur d'elasticsearch et récupérer le résultat dans le dataframe df_sensor
    req_sensor = requests.post("http://localhost:9200/_sql", data=query_sensor, headers={'Content-Type':'application/json'})
    response_sensor = req_sensor.json()
    df_sensor = pd.DataFrame(response_sensor['rows'],
                    columns=[d['name'] for d in response_sensor['columns']])
    
    
    # Cette partie de code commentée est dédiée aux cas où la requête SQL sur les données sensor renvoie plus de 10 000 lignes comme résultat
    '''
    # Tant qu'il y a des lignes à récupérer 
    while (response_sensor['rows'] != []):

        # Récupère le curseur qui pointe sur les 10000 lignes suivantes
        cursor= json.dumps({ "cursor": response_sensor['cursor']})
        
        # Renvoyer une requête POST au serveur de Elasticsearch en passant en paramètre le curseur pour récupérer les lignes suivantes
        request = requests.post("http://localhost:9200/_sql", data=cursor, headers={'Content-Type':'application/json'})
        
        # Récupérer le résultat sous forme json
        response_sensor = request.json()

        # Stocker les lignes récupérées dans un dataframe qui a les mêmes colonnes que le premier dataframe contenant le résultat de la première requête SQL sur les données sensor
        df2 = pd.DataFrame(response_sensor['rows'],
                        columns=df_sensor.columns)
        # Mettre à jour le contenu du dataframe df_sensor avec les nouvelles lignes récupérées
        frames = [df_sensor,df2]
        df_sensor = pd.concat(frames)
    '''
                
    #créer le dataframe qui joint les deux dataframe précédents par rapport au champ "myNodeId" des identifiants des noeuds
    df_merged = pd.merge(df_network, df_sensor, on='myNodeId')

    return df_merged


def flat(measures,liste):
    for sublist in measures:
            liste.append(sublist)
    return liste

#####################################################################################################################
# - Fonction qui crée la table pivot à partir des dimensions et mesures choisies                                    #
#                                                                                                                   #
#####################################################################################################################
def olap_configuration():

    global liste
    global i
    global label
    global text
    #récupérer les dimensions choisies
    my_dimension_temps = choose_dimension_temps.get()
    my_dimension_node = choose_dimension_node.get()
    my_dimension_spatiale = choose_dimension_spatiale.get()
    # Récupérer la liste des mesures dans une chaine de caractères sous la forme "mesure1,mesure2..."
    my_measure = str(measures_listbox.get(0))
    for item in range(1,len(measures_listbox.curselection())):
       my_measure = str(measures_listbox.get(item))+","+my_measure 


    #Créer le dataframe utilisé dans la table pivot
    df = joined_data(my_dimension_temps,my_measure)

    booleen = True 
    # choisir les champs à garder du dataframe df en distinguant les cas selon les dimensions choisies par l'utilisateur (il se peut
    # que l'utilisateur ne choisisse pas des dimensions)  
    if (my_dimension_spatiale) :
        if(my_dimension_node) :
            if (my_dimension_temps):
                final_data = df[flat(my_measure.split(','), [my_dimension_temps,my_dimension_node,my_dimension_spatiale])]
                
            else :
                final_data = df[[my_dimension_node,my_dimension_spatiale,my_measure.split(',')]]
        elif (my_dimension_temps):
            final_data = df[[my_dimension_temps,my_dimension_spatiale,my_measure.split(',')]]
        else :
            final_data = df[[my_dimension_spatiale,my_measure.split(',')]]
    else :
        if(my_dimension_node) :
            if (my_dimension_temps):
                final_data = df[[my_dimension_temps,my_dimension_node,my_measure.split(',')]]
            else :
                final_data = df[[my_dimension_node,my_measure.split(',')]]
        elif (my_dimension_temps):
            final_data = df[[my_dimension_temps,my_measure.split(',')]]
        
        #si l'utilisateur n'a choisi aucune dimension
        else : 
            
            booleen = False

    # générer l'interface de la table pivot si l'utilisateur a choisi au moins une dimension
    if (booleen) :
        pivot_ui(final_data ,rows=[my_dimension_temps,my_dimension_node,my_dimension_spatiale],exclusions={final_data.columns[0] : ["null"]},outfile_path='cube.html')
        HTML('cube.html')
        # Ouvrir l'interface dans le navigateur
        webbrowser.open("cube.html")
    # si l'utilisateur n'a choisi aucune dimension, un message d'erreur s'affiche
    else: 
        error = Label(button_frame, text="Il faut choisir des dimensions", font=("Courrier", 14),bg='#4065A4',fg='red')
        error.pack()
    # réinitialiser la liste des saisies dans le filtre géospatial (liste des points + affichage des points saisis dans la variable text) 
    liste = []
    i=0
    text = ""
    label.config(text=text)
    

#Configuration de l'interface graphique 

#---------------------------------- partie des dimensions et mesures --------------------------------------------

#dimensions---------------------------------------------------------------------------

dimension_temps = [
    "Annee_sensor",
    "mois_sensor",
    "jour_sensor",
    "packetTimeSensor"
    
]

dimension_node = [
    "myNodeId",
    "nodeType"
]

dimension_spatiale = [
    "Coord"
]

# Time dimension
dimension_temps_label = Label(dimension_frame, text="Dimension Temps", font=("Courrier", 14),bg='#4065A4',fg='white')
dimension_temps_label.pack(pady=10)
choose_dimension_temps = ttk.Combobox(dimension_frame, width = 27, value=dimension_temps)
choose_dimension_temps.pack()

#Node dimension
dimension_node_label = Label(dimension_frame, text="Dimension Noeud", font=("Courrier", 14),bg='#4065A4',fg='white')
dimension_node_label.pack(pady=10)
choose_dimension_node = ttk.Combobox(dimension_frame, width = 27, value=dimension_node)
choose_dimension_node.pack()

#Spatial dimension
dimension_spatiale_label = Label(dimension_frame, text="Dimension Spatiale", font=("Courrier", 14),bg='#4065A4',fg='white')
dimension_spatiale_label.pack(pady=10)
choose_dimension_spatiale = ttk.Combobox(dimension_frame, width = 27, value=dimension_spatiale)
choose_dimension_spatiale.pack()

#mesures-------------------------------------------------------------------------------

mesures = [
    "temperature",
    "humidity",
    "light",
    "battery",
    "decagon1",
    "degacon2",
    "decagon3",
    "watermark1",
    "watermark2",
    "watermark3",
    "watermark4"
]

measure_label = Label(dimension_frame, text="Mesure", font=("Courrier", 14),bg='#4065A4',fg='white')
measure_label.pack(pady=10)

my_scrollbar2 = ttk.Scrollbar(dimension_frame, orient=VERTICAL)

measures_listbox = Listbox(dimension_frame,width=30,height=7,selectmode=MULTIPLE,exportselection=0,yscrollcommand=my_scrollbar2.set)

my_scrollbar2.config(command=measures_listbox.yview)
my_scrollbar2.pack(side=RIGHT, fill=Y)
measures_listbox.pack(fill=X)
for item in mesures:
    measures_listbox.insert(END,item)

#------------------------------------- Bouton valider ----------------------------------------------

validate_button = Button(button_frame,text = "Valider",font=("Courrier", 14),bg='white',fg='#4065A4',command=olap_configuration)
validate_button.pack(pady=25,fill =X,expand=1)
booleen = True

#------------------------------------- partie du filtre géospatial ---------------------------------
# Geospatial queries

liste = []
label = Label(geospatial_frame, font=("Courrier", 11),bg='#4065A4',fg='white')
i=0
text=""
def generate_points():
    global i
    global text
    global liste
    i = i+1
    liste_lat_lon = []
    lon = float(enter_lon.get())
    lat = float(enter_lat.get())
    
    liste_lat_lon.append(lon)
    liste_lat_lon.append(lat)
    liste.append(liste_lat_lon)
    enter_lon.delete(0,'end')
    enter_lat.delete(0,'end')
    text = text + "Point "+str(i)+": "+str(liste[i-1]) + "\n"
    label.config(text=text)
    label.grid(row=5+len(liste),column=0,pady=5)
    
    


geo_label = Label(geospatial_frame, text="Calcul géospatial", font=("Courrier", 16),bg='#4065A4',fg='white')
geo_label.grid(row=0,column=0,pady=10)

lon_label = Label(geospatial_frame, text="Longitude :", font=("Courrier", 12),bg='#4065A4',fg='white')
lon_label.grid(row=3,column=0,pady=10)
enter_lon = Entry(geospatial_frame)
enter_lon.grid(row=3,column=1,pady=10)
lat_label = Label(geospatial_frame, text="Latitude :", font=("Courrier", 12),bg='#4065A4',fg='white')
lat_label.grid(row=4,column=0,pady=10)
enter_lat = Entry(geospatial_frame)
enter_lat.grid(row=4,column=1,pady=10)
generate_button = Button(geospatial_frame,text = "Ajouter le point",font=("Courrier", 12),bg='white',fg='#4065A4',command= generate_points)
generate_button.grid(row=5,column=0)



relations =[
    "INTERSECTS",
    "CONTAIN",
    "WITHIN",
    "DISJOINT"
]
relation_label = Label(geospatial_frame, text="Relation (>= 3 points) :", font=("Courrier", 11),bg='#4065A4',fg='white')
relation_label.grid(row=1,column=0,pady=10)
choose_relation = ttk.Combobox(geospatial_frame, value=relations)
choose_relation.grid(row=1,column=1,pady=10)
distance_label = Label(geospatial_frame, text="Distance (1 point) :", font=("Courrier", 11),bg='#4065A4',fg='white')
distance_label.grid(row=2,column=0,pady=10)
enter_distance = Entry(geospatial_frame)
enter_distance.grid(row=2,column=1,pady=10)


# ----------------------------------------- Ajuster la disposition des frames + ajout d'un onglet menu ----------------------------

geospatial_frame.grid(row=0,column=3,padx=60,pady=20,sticky=N+S+E+W)
dimension_frame.grid(row=0,column=0,padx=20,pady=20,sticky=N+S+E+W)
button_frame.grid(row= 1,column=2,padx=20,pady=20,sticky=N+S+E+W)
second_frame.pack(fill="both", expand=True)



# create menu
menu_bar = Menu(main_frame)

#first menu
main_menu = Menu(menu_bar,tearoff=0)
main_menu.add_command(label="Quitter",command = root.quit)
menu_bar.add_cascade(label="Menu",menu=main_menu)

# Add the menu to the main window "root"
root.config(menu=menu_bar)
root.mainloop()