# Python-Web-Site-Helper

Version 1.3.3

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

1.0.4 :

Augmentation du buffsize, pour permettre plus de cookies, ou plus de données a travers les requetes/formulaires.
Ajout d'un système pour enlever un cookie.
Compatibilité accrue pour le contenu.

1.0.5 :

Ajout du décorateur @need_cookies().

1.1.0 :

Refonte d'une partie de la reception des requetes. Mise en place de la possibilité de fermer le programme normalement (Ctrl+C)

1.1.1:

Correction de différents bugs. L'on est plus obligé de passer en argument "user" si l'on ne l'utilise pas. Utilisation de "files/truc.css" pour demander un fichier, plus "file/truc.css" -> mise en accord avec le nom du dossier

1.1.2:

Ajout d'un message dans la console si l'on ne retourne rien. Ajout de la possibilité de retourner directement une réponse encodée.

1.1.3:

Corrections de bugs. Possibilité de faire télécharger des fichiers beaucoup plus facilement. Ajout de la recherche par défaut d'un favicon dans les fichiers

1.2.0:

Changement en partie du fonctionnement du Framework, ajout d'une façon d'avoir des url non totalement déterminés (ex : "/user/{var}/profile", "/product/{var}") avec en argument de la fonction var. 

1.3.0:

Ajout de commentaires pour expliquer le fonctionnement du framework. Reglage de nombreux bugs.

1.3.1:

L'on peut désormais utiliser des accents dans les retours/templates.

1.3.2:

Réglage de bugs.

1.3.3:

Amélioration de l'utilisation du processeur : Consomme moins de CPU


<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
