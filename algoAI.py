from __future__ import division
from sklearn import tree
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from kmodes import kprototypes
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.decomposition import PCA
from time import clock
import sql
import numpy as np
import random
import pandas as pd
import gap
from gap import gap

def completeQuery(datasetQuery, database, maxcompletions):
    """
    Applique le framework complet à partir d'une requête sql initiale
    :param datasetQuery: la requête SQL initiale
    :param database: le nom de la base de données à laquelle soumettre la requête
    :param maxcompletions: nombre max de complétions à obtenir
    :return: le cluster que chaque complétion représente, les complétions, et la taille des résultats
    """

    data, header = sql.return_dataset_from_query(datasetQuery, database)

    if len(data)<2:
        print("Pas assez de données pour l'analyse")
    else:
        keys = sql.get_keys(database)
        categorial_index, dataset, header, scaler = preprocess(data, header, keys)
        labels = clustering(dataset, maxcompletions)
        if len(labels) <= 0:
            return [], [], []
        else:
            clf = decision_tree(dataset, labels, maxcompletions)

    queryClass, sqlQueries, sizes = tree_to_code(clf, header, datasetQuery, database, scaler)

    return queryClass, sqlQueries, sizes

def preprocess(data, headers, keys):
    """
    Remove unnecessary attributes and non numerical ones, as well as keys, normalize attributes
    :param data: dataset to process
    :param headers: attributes names in the dataset
    :param keys: name of all attribute that are primary of foreign keys
    :return: index of categorial attributes, the processed dataset, remaining attributes names, and scaler used for normalization
    """
    print(headers)
    nonNumerical = []
    # Déterminer quelle colonnes du dataset contiennent des attributs non numeriques
    for tuple in data:
        i = 0
        for value in tuple:
            try:
                float(value)
            except ValueError:
                if i not in nonNumerical:
                    nonNumerical.append(i)
            i += 1

    columnsToKeep = []
    toDeleteInTree = []

    for k in keys:
        if k in headers:
            nonNumerical.append(headers.index(k))

    for i in range(len(data[0])):
        if i in nonNumerical:
            toDeleteInTree.append(i)
        else:
            columnsToKeep.append(i)

    headers = [headers[i] for i in range(len(headers)) if i not in toDeleteInTree]
    dataset = [[tuple[i] for i in columnsToKeep] for tuple in data]
    categorial_index = nonNumerical

    scaler = StandardScaler()
    dataset = scaler.fit_transform(dataset)

    return categorial_index, dataset, headers, scaler


def clustering(data, maxcompletions):
    """
    Cluster data
    :param data: the dataset containing tuples to cluster
    :param maxcompletions: number of clusters
    :return: a list with the cluster each tuple belongs to
    """
    data = np.asarray(data)
    km = KMeans(n_clusters=maxcompletions)
    clusters = km.fit_predict(data)
    return clusters


def decision_tree(attributes, labels, maxleafnodes):
    """
    Applique un arbre de décision à un jeu de données labellisées (labels normalement issus du clustering)
    :param attributes: données à traiter sous forme d'un tableau 2D avec une ligne par donnée
    :param labels: le label correspondant à chaque ligne du jeu de données sous forme d'un tableau 1D
    :return: l'arbre de décision sous forme d'un objet de la librairie sklearn
    """
    clf = tree.DecisionTreeClassifier(max_leaf_nodes=maxleafnodes)
    clf = clf.fit(attributes, labels)
    return clf

def tree_to_code(clf, feature_names, beginSQL, database, scaler):
    """
    Transforme l'arbre de décision en une liste de requête SQL
    :param clf: l'arbre de décision sous forme d'un objet de la librairie sklearn
    :param feature_names: la liste des attributs sur lequel l'arbre de décision a fait son apprentissage
    :param beginSQL: la requête SQL a compléter avec les règles issues de l'arbre
    :param database: la base de donnée à interroger pour les requêtes
    :return: trois listes avec le cluster de chaque requête, la requête complétion, et la taille de son résultat
    """
    left = clf.tree_.children_left
    right = clf.tree_.children_right
    threshold = clf.tree_.threshold
    features = [feature_names[i] for i in clf.tree_.feature]

    # get ids of child nodes
    idx = np.argwhere(left == -1)[:, 0]

    def recurse(left, right, child, statements):
        if len(statements) == 0:
            statements.append(np.argmax(clf.tree_.value[child][0]) + 1)
        if child in left:
            parent = np.where(left == child)[0].item()
            split = ' <= '
        else:
            parent = np.where(right == child)[0].item()
            split = ' > '

        value = threshold[parent]
        indexOfFeature = feature_names.index(features[parent])
        numArray = [0 for i in range(len(feature_names))]
        numArray[indexOfFeature]=value
        numArray = scaler.inverse_transform(numArray)
        value = numArray[indexOfFeature]
        statements.append(str(features[parent]) + split + str(round(value, 150)))

        if parent == 0:
            return statements
        else:
            return recurse(left, right, parent, statements)

    sqlQueries = []
    queryClass = []

    for child in idx:
        statements = []
        recurse(left, right, child, statements)
        if 'where' in beginSQL:
            finalQuery = beginSQL + ' and '
        else:
            finalQuery = beginSQL + ' where '
        queryClass.append(statements[0])
        for s in statements[::-1]:
            finalQuery += (str(s) + ' and ')
        sqlQueries.append(finalQuery[:-11])

    i = 0
    sizes = []
    for q in sqlQueries:
        countQuery = 'Select count(*) from ' + q.split(' from ')[1]
        nbTuples = sql.execute_query(countQuery, database)[0][0][0]
        sizes.append(nbTuples)
        i += 1

    return queryClass, sqlQueries, sizes
