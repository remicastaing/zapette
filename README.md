# Zapette

**Contrôle parental de la télé pour Home Assistant.** Les enfants allument eux‑mêmes la télévision
en tapant leur code personnel sur un clavier Zigbee, dans la limite d'un **quota quotidien** et de
**plages horaires** choisies par les parents. Quand le temps est écoulé, la prise de la télé est
coupée.

![Zapette](custom_components/zapette/brand/icon.png)

## Ce que fait Zapette

- Un **code par enfant** sur le clavier : la prise de la télé s'allume si l'enfant est dans une de
  ses plages horaires et qu'il lui reste du temps ; sinon, le clavier signale le refus.
- **Quota par jour de la semaine** et jusqu'à 4 plages horaires par jour, pour chaque enfant.
- **Avertissement** avant la coupure (bip du clavier si possible), puis **coupure automatique** :
  quota épuisé, fin de plage, minuit, télé en veille.
- **Codes parents** : télé sans limite (coupure de sécurité réglable), fin d'une session enfant,
  déblocage du clavier.
- **Protection** : la prise allumée hors session est recoupée ; le clavier se verrouille après
  plusieurs codes faux. Les codes sont hachés, jamais affichés ni journalisés.
- **Historique** sur 90 jours, en calendrier : qui a regardé, quand, combien de temps par jour et
  par semaine, et les incidents (refus, prise injoignable…).
- **Panneau Zapette** dans la barre latérale (administrateurs) : enfants, quotas et plages,
  historique et réglages. En français et en anglais, sur ordinateur comme sur téléphone.
- Entités, actions et événements Home Assistant pour vos tableaux de bord et automatisations.

## Matériel requis

| Élément | Rôle | Remarques |
|---|---|---|
| Coordinateur Zigbee + **Zigbee2MQTT** | Réseau Zigbee | Zapette utilise Zigbee2MQTT, elle ne gère pas le dongle |
| **Prise Zigbee** | Alimente la télé | Exposée comme interrupteur ; **mesure de puissance conseillée** (détection de veille) |
| **Clavier Zigbee à code** | Saisie des codes | Doit remonter le code saisi (`action_code`) ; testé avec le frient KEPZB‑110 |

Une seule prise et un seul clavier par télévision ; plusieurs télévisions possibles (une instance de
Zapette chacune).

## Prérequis

- Home Assistant **2026.9.0** ou plus récent.
- L'intégration **MQTT** configurée avec le broker utilisé par Zigbee2MQTT.
- [HACS](https://hacs.xyz) installé.

## Installation par HACS

Zapette s'installe comme **dépôt personnalisé** :

1. Dans Home Assistant, ouvrir **HACS**, menu **⋮** en haut à droite → **Dépôts personnalisés**.
2. Dépôt : `https://github.com/remicastaing/zapette`, type : **Intégration** → **Ajouter**.
3. Rechercher **Zapette** dans HACS, l'ouvrir, puis **Télécharger** (dernière version proposée).
4. **Redémarrer Home Assistant** (Paramètres → Système → Redémarrer).

## Configuration

1. **Paramètres → Appareils et services → Ajouter une intégration → Zapette**.
2. Donner un nom à la télévision, choisir la prise (et son capteur de puissance s'il existe), le
   clavier Zigbee2MQTT (un test de saisie vérifie la réception), puis le code parent.
3. Ouvrir **Zapette** dans la barre latérale : ajouter les enfants (prénom, code, quotas, plages).

Tout se règle ensuite dans le panneau (onglet **Réglages**) ou par **Configurer** sur la page de
l'intégration : avertissement avant coupure, anti‑essais du clavier, veille, codes parents…

## Mise à jour

HACS signale les nouvelles versions de Zapette (avec leurs notes) : **Mettre à jour**, puis
redémarrer Home Assistant. Le paramétrage et l'historique sont conservés.

## Bon à savoir

- Un redémarrage de Home Assistant termine la session en cours et coupe la prise : l'enfant retape
  son code.
- En cas de doute (prise injoignable, erreur), Zapette coupe la prise plutôt que de la laisser
  allumée.
- Dans les journaux, l'historique et les diagnostics, aucun code n'apparaît.

## Licence

[MIT](LICENSE).
