import numpy as np
import simplejson
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,precision_score,recall_score
import csv


def find_precision(model,X_test,Y_test):
	return precision_score(model.predict(X_test),Y_test)

def find_recall(model,X_test,Y_test):
	return recall_score(model.predict(X_test),Y_test)

def find_auc(model,pro,Y_test):
	#X_test.
	return roc_auc_score(Y_test,pro)

if __name__ == '__main__':
	f = open("multilayer_layer1.emb","r")
	# Load The EdgeList File 
	X = []
	Y = []
	dic = {}
	for l in f:
		l = l.strip().split(" ")
		l[0] = int(l[0])
		temp = [float(l1) for l1 in l[1:]]
		dic[l[0]] = np.array(temp)

	X_train = []
	Y_train = []
	print((dic[396]))
	edges_train=csv.reader(open("Layer1_Edgelist_Eval/training_layer1_edges.txt","r"),delimiter=';')
	no_edges_train=csv.reader(open("Layer1_Edgelist_Eval/training_layer1_noedges.txt","r"),delimiter=';')
	cot=0

	for l in edges_train:
		#print(int(l[0]))
		X_train.append(dic[int(l[0])]+dic[int(l[1])])
		Y_train.append(1)
		
	for l in no_edges_train:
		try:
			X_train.append(dic[int(l[0])]+dic[int(l[1])])
			Y_train.append(0)
		except:
			cot=cot+1
			continue
	X_test = []
	Y_test = []
	print("Train Done")
	edges_test=csv.reader(open("Layer2_Edgelist_Eval/test_edge.txt","r"),delimiter=';')
	no_edges_test=csv.reader(open("Layer2_Edgelist_Eval/test_noedge.txt","r"),delimiter=';')

	for l in edges_test:
		try:
			X_test.append(dic[int(l[0])]+dic[int(l[1])])
			Y_test.append(1)
		except:
			cot=cot+1
			continue
	for l in no_edges_test:
		try:
			X_test.append(dic[int(l[0])]+dic[int(l[1])])
			Y_test.append(0)
		except:
			cot=cot+1
			continue
	print(len(X_test[0]))
	print("Test Done")
	clf = LogisticRegression(C=0.8,random_state = 0,solver = "lbfgs",n_jobs = 16)
	#print(X_train)
	model = clf.fit(X_train,Y_train)
	print("predict_proba")
	prob=[]
	for i in model.predict_proba(X_test):
		prob.append(i[0])
	
	#print(cot)

	print(find_precision(model,X_test,Y_test))
	print(find_recall(model,X_test,Y_test))
	print(find_auc(model,prob,Y_test))

	print(cot)