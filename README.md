# ProjetElasticsearch

Avant d'exécuter le code "OLAP.py", vérifier bien que vous avez lancer le serveur d'elasticsearch à partir du répertoire bin du répertoire de elasticsearch téléchargé.

# Intégration des données network
1- Lancer le script "network.py" pour créer l'index network avec son mapping (vous pouvez vérifier la création sur kibana -> index management ).
2- sur le fichier logstash_network.conf, dans la partie "input" bien définir le chemin du fichier csv contenant les données network dans "path".
3- Sur un terminal (ou cmd si windows) lancer à partir du répertoire bin du répertoire de logstash téléchargé la commande : logstash -f chemin-du-fichier-logstash_network.conf
4- Attendre jusqu'à ce que toutes les lignes soient intégrées (les lignes insérées sont affichées sur le terminal au fur et à mesure) : la vérification peut également se faire sur kibana -> index management pour voir combien de docs sont insérés dans l'index.

# Intégration des données sensor
1- sur le fichier logstash_sensor.conf, dans la partie "input" bien définir le chemin du fichier csv contenant les données sensor dans "path".
2- Sur un terminal (ou cmd si Windows), lancer à partir du répertoire bin du répertoire de logstash téléchargé la commande : logstash -f chemin-du-fichier-logstash_sensor.conf
3- Attendre que l'insertion soit finie. Pour les données sensor contenant des millions de lignes, le traitement peut prendre plusieurs heures selon la puissance de l'ordinateur utilisé (les lignes insérées sont affichées sur le terminal au fur et à mesure) : la vérification peut également se faire sur kibana -> index management pour voir combien de docs sont insérés dans l'index.

# Exécution du code OLAP.py
- Installer la librairie tkinter sur python avec pip install si elle ne l'est pas déjà. Pour vérifier, il suffit de lancer sur un shell python :
>>> import tkinter
>>> tkinter._test()

si tout se passe bien, une petite fenêtre s'affiche sur l'écran.

- Installer la librairie pivottablejs : pip install pivottablejs
- Installer la librairie d'elasticsearch : pip install elasticsearch
- Au cas où il y a des erreurs d'import lors de la compilation il suffit d'installer la librairie qui est sujet de l'erreur à l'aide de "pip".
- Finalement, exécuter le code, l'interface graphique va s'afficher pour effectuer les requêtes OLAP.
