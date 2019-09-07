# Python-Web-Site-Helper

Version 1.0.2

ChangeLog : 

1.0.0 :

Création du projet.
Système de requetes, traitement des requetes, retour à l'aide de templates, création d'url, lancement et arret du site, redirections, récupération de la méthode de requete et de l'url (user.request).
Capacités de supporter plusieurs requetes simultanées.
Création du serveur avec host et port.

1.0.1 :

Ajout du formatage des templates.
Capacité à mettre un cookie et récupérer les cookies des clients.
Autorisation de certaines méthodes spécifiques avec le décorateur @methods()


1.0.2 :

Ajout de la capacité à supporter les requetes post ainsi que get a formulaire.
Récupération des formulaires (user.request.form)
Ajout de la possibilité de mettre des liens css et js dans les templates.
Refonte de la réponse -> Plus forcément "text/html".
Maintenant cela répond en fonction des réponses acceptées.

1.0.3 :

Capacité à import d'autres template dans un template avec &&&filename&&& dans le fichier html.
Possibilité de télécharger le contenu (avec l'attribut download de la balise a).
