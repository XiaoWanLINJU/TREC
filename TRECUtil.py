# -*-encoding:utf-8 -*-
__author__ = 'XiaoWanLI' 
import codecs 
import numpy
import os

#无序,feature需要再处理 
def svm2pair(instanceList,sorceFile, index, classList):
    """
    args: 
    index: if null, just pair, or, shuffle as index indicate
    classList: the instance's class, sorted from most relevant to least relevant 
    """
    if len(index) != 0:
        fw = codecs.open(sorceFile + ".shuffle2.cntk","a")
    else:
        fw = codecs.open(sorceFile + ".cntk","a")
    featurebin = [[] for x in range(len(classList))]
    #print 'sorce file', sorceFile
    for instance in instanceList:
        label, features = instance
        #print features
        #features = [f.split(":")[1] for f in features]
        if len(index) != 0:
            features = shuffle_single_feature(features, index)
        for i in range(len(classList)):
            if label == classList[i]:# the lower index, the higher relevant
                featurebin[i].append(" ".join(features))
    for i in range(len(classList)):
        posinslist = featurebin[i]
        for j in range(i + 1, len(classList)):
            neginslist = featurebin[j]
            for posins in posinslist:
                for negins in neginslist:
                    fw.write(posins + " " + negins + " 1.0\n")
                    fw.write(negins + " " + posins + " 0.0\n")
    fw.close()

def svm2pair4test(instanceList, testFile, index):
    if len(index) != 0:
        fw = codecs.open(testFile + ".shuffle2.cntktest","a")
    else:
        fw = codecs.open(testFile + ".cntktest","a")
    for i in range(len(instanceList)):
        labeli, featuresi = instanceList[i]
        featuresi = [f.split(":")[1] for f in featuresi]
        if len(index) != 0:
            featuresi = shuffle_single_feature(featuresi, index)
        for j in range(len(instanceList)):
            if i != j:
                labelj, featuresj = instanceList[j]
                featuresj = [f.split(":")[1] for f in featuresj]
                if len(index) != 0:
                    featuresj = shuffle_single_feature(featuresj, index)
                if float(labeli) > float(labelj):
                    fw.write(" ".join(featuresi) + " " + " ".join(featuresj) + " 1.0\n")
                else:
                    fw.write(" ".join(featuresi) + " " + " ".join(featuresj) + " 0.0\n")
    fw.close()

def getInstanceScore(instanceList, testFile):
    """
    get instance score from pairwise score by one against all
    """
    global count
    #print count
    fw = codecs.open(testFile + ".score","a")
    score = [[0 for i in range(len(instanceList))] for i in range(len(instanceList))]
    for i in range(len(instanceList)):
        for j in range(len(instanceList)):
            if i != j:
                score[i][j] = numpy.exp(res[count][1])/sum([numpy.exp(x) for x in res[count]])
                count += 1
        fw.write(str(sum(score[i]))+" \n")
    fw.close()

def get_instance_list_fromSVM(sorceFile, testFile,instruct, index, classList):
    """
    get instance list form svm format, which is used to get pairs
    Args:
        sorceFile: svm format file
        testFile: cntk format file
        instruct: pair for test or train or just get instance
    """
    fr = codecs.open(sorceFile,"r")
    currentQid = ""
    line = fr.readline()
    instanceList = []
    while line:
        tokens = str(line.strip().split('#')[0]).split()
        label = tokens[0]
        featureList = tokens[2:]
        if currentQid == "":
            currentQid = tokens[1].split(":")[1]
        # print currentQid, tokens[1].split(":")[1]
        if currentQid != tokens[1].split(":")[1]:
            currentQid = tokens[1].split(":")[1]
            #print currentQid
            if instruct == "2pair":
                svm2pair(instanceList,sorceFile, index, classList)
            elif instruct == "2pair4test":
                svm2pair4test(instanceList,sorceFile, index)
            elif instruct == "score":
                getInstanceScore(instanceList, testFile)
            instanceList = []

        instanceList.append((label, featureList))
        line = fr.readline()
    if instruct == "2pair":
        svm2pair(instanceList,sorceFile, index, classList)
    elif instruct == "2pair4test":
        svm2pair4test(instanceList,sorceFile, index)
    elif instruct == "score":
        getInstanceScore(instanceList, testFile)
    fr.close()

def getRes(fileName):
    print fileName
    global res
    res = []
    fr = open(fileName,"r")
    line = fr.readline()
    while line:
        ress = line.split()
        res.append([float(x) for x in ress])
        line = fr.readline()

def get_infor_data(file_name):
    query_doc_relevant = {}
    query_doc_irrelevant = {}
    fr = codecs.open(file_name,"r")
    line = fr.readline()
    while line:
        tokens = line.split()
        qid = str(tokens[1]).split(":")[1]
        if qid not in query_doc_relevant:
            query_doc_relevant[qid] = 0
            query_doc_irrelevant[qid] = 0
        if tokens[0] == "0":
            query_doc_irrelevant[qid] += 1
        else:
            query_doc_relevant[qid] += 1
        line = fr.readline()
    print len(query_doc_relevant.keys())
    for key in query_doc_relevant.keys():
        print key, query_doc_relevant[key], query_doc_irrelevant[key]

def terc_cntk2score(test, fold, res_delix, wlist, clist):
    global count
    global res
    print test, res_delix,"2score"
    for w in wlist:
        for c in clist:
            try:
                count = 0
                if test.__contains__("validationset"):
                    source_file = "/validationset.txt"
                    test_file = str(fold) + "/w" + str(w) + "c" + str(c) + res_delix
                elif test.__contains__("trainingset"):
                    source_file = "/trainingset.txt"
                    test_file = str(fold) + "/w" + str(w) + "c" + str(c) + res_delix
                #elif test.__contains__("test"):#if only use if, validationset.txt.cntktest may be confusion
                #    source_file = "/testset.txt"
                #    test_file = str(fold) + "/w" + str(w) + "c" + str(c) + res_delix
                elif test.startswith('mt'):
                    source_file = '/' + str(test.split('.')[0]) + '.bleusvm'
                    test_file = str(fold) + "/lowerw" + str(w) + "c" + str(c) + res_delix
                print test_file, source_file
                getRes(test_file)
                get_instance_list_fromSVM(str(fold) + "/" + source_file,test_file,"score", [], [])
            except IOError as err:
                print "IOError: {0}".format(err)
def terc_cntk2score_ff(test, fold, res_delix, hlist, hpconfig):
    global count
    global res
    print test,fold,"2score"
    for h in hlist:
        try:
            count = 0
            if test == "validationset.txt.cntktest":
                source_file = "/validationset.txt"
                test_file = str(fold) + "/lowerlinearh" + str(h) + res_delix
            if test == "trainingset.txt.cntktest":
                source_file = "/trainingset.txt"
                test_file = str(fold) + "/h" + str(h) + res_delix
            if test == "test":
                source_file = "/testset.txt"
                test_file = str(fold) + "/h" + str(h) + res_delix
            if test.startswith('mt'):
                source_file = '/' + str(test.split('.')[0]) + '.bleusvm'
                test_file = str(fold) + hpconfig + str(h) + res_delix
            getRes(test_file)
            get_instance_list_fromSVM(str(fold) + "/" + source_file,test_file,"score", [], [])
        except IOError as err:
            print "IOError: {0}".format(err)

import random

def shuffle_single_feature(feature, index):
    """feature and index have same length
    """
    construct_f = [0 for x in feature]
    for i in range(len(feature)):
        construct_f[i] = feature[index[i] - 1]
    return construct_f

def shuffle_feature(file_list, target_path, index_list, suffix):
        if os.path.isdir(target_path):
            pass
        else:
            os.mkdir(target_path)
        fwt = codecs.open(target_path + 'index.txt', 'a')
        for index in index_list:
            fwt.write('\t'.join([str(x) for x in index]) + '\n')
        fwt.close()
        for train_file in file_list:
            fr = codecs.open(target_path + train_file,  'r')
            fw = codecs.open(target_path + train_file + '.shuffle' + suffix,  'w')
            line = fr.readline()
            while line:
                features = line.lstrip().split()
                construct_all_left = []#first instance
                construct_all_right = []#second instance
                for index in index_list:
                    construct_f_left = [0 for i in range(44)]
                    construct_f_right = [0 for i in range(44)]
                    for i in range(44):
                        construct_f_left[i] = features[index[i] - 1]# index given start at 1
                        construct_f_right[i] = features[44 + index[i] - 1]
                    construct_all_left = construct_all_left + construct_f_left
                    construct_all_right = construct_all_right + construct_f_right
                fw.write('\t'.join(construct_all_left) + '\t' + '\t'.join(construct_all_right) + '\t' + features[-1]+ '\n')
                line = fr.readline()
            fr.close()
            fw.close()
if __name__ == "__main__":
    #index = [2, 9, 28, 32, 3, 10, 15, 16, 17, 18, 29, 33, 4, 11, 19, 20, 21, 22, 23, 24, 25, 26, 30, 34, 6, 37, 5, 31, 35, 12, 1, 8, 14, 36, 7, 38, 13, 27, 39, 40, 41, 42, 43, 44]
#get_instance_list_fromSVM('../mt/run2/mt02', '', '2pair4test', [])
#    index = [15, 16, 17, 18, 29, 33, 3, 10, 2, 9, 4, 11, 25, 26, 30, 34, 23, 28, 32, 21, 22, 19, 20, 24, 1, 5, 31, 35, 12, 6, 37, 7, 38, 36, 8, 14, 13, 27, 40, 41, 39, 42, 44, 43]
    #get_instance_list_fromSVM('../TREC2003/fold1/testset.txt', '', '2pair4test', [], ['1', '0'])
    #index = [27, 33, 35, 10, 29, 1,  13, 9,  37, 20, 25, 18, 16, 36, 5,  4, 43, 24, 19, 38, 40, 8,  23, 12, 31, 44, 39, 34, 26, 15, 30, 21, 41, 11, 22, 6,  14, 28, 3,  17, 7,  42, 2,  32]
#    index = [x for x in range(1, 45)] 
    #index = [35, 14, 29, 39, 44, 6,  15, 1,  28, 3,  10, 22, 32, 11, 42, 21, 7,  4,  36, 2,  37, 20, 23, 24, 13, 34, 38, 30, 16, 9,  18, 25, 12, 31, 17, 33, 27, 5,  8,  43, 26, 19, 41, 40] 
#    random.shuffle(index)
#    index5 = [37, 38, 36, 33, 34, 32, 35, 29, 30, 28, 31, 13, 27, 14, 18, 26, 22, 17, 25, 21, 15, 23, 19, 10, 9, 11, 12, 40, 41, 39, 42, 44, 43, 8, 6, 7, 3, 2, 4, 5, 16, 20, 24, 1] 
#    index_list1 = []
#    index_list1.append(index)
#    index6 = [35, 31, 12, 5, 34, 30, 26, 25, 23, 11, 4, 24, 40, 41, 39, 36, 7, 37, 38, 13, 27, 42, 44, 43, 22, 21, 19, 20, 32, 28, 9, 2, 6, 33, 29, 18, 17, 15, 10, 3, 16, 14, 8, 1]
##    #shuffle_feature(['validationset.txt.cntktest'], '../TREC2004/fold2/', index_list, '4')
#    index_list2 = []
#    index_list2.append(index)
    for fold in range(1, 2):
#            print path, fold
#            shuffle_feature(['test'], path + 'fold' + str(fold) + '/', index_list1, '5')
#            shuffle_feature(['test'], path + 'fold' + str(fold) + '/', index_list2, '6')
            get_instance_list_fromSVM('../TREC2003/fold' + str(fold) + '/validationset.txt','', '2pair4test', [], [] )
#           shuffle_feature(['test'], path + 'fold' + str(fold) + '/', index_list, '3')
#    foldlist = ['../mt/jhj100/top10_run1/', '../mt/jhj100/top10_run2/', '../mt/jhj100/top10_run3/']
#    filelist = ['4', '5', '6']
#    for fd in foldlist:
#        for fn in filelist:
#            print fd, fn
#            get_instance_list_fromSVM(fd + '/mt0' + fn + '.bleusvm', fd + '/mt0' + fn + '.cntktest', '2pair4test',  [],  ['1', '0'])
    #print '1'
    #get_instance_list_fromSVM('../mt/jhj100/best_worst_run2/mt02.bleusvm',  '../mt/best_worst_run2/mt02.cntktest', '2pair4test',  [],  ['1', '0'])
    #print '2'
    #get_instance_list_fromSVM('../mt/jhj100/best_worst_run3/mt02.bleusvm',  '../mt/best_worst_run3/mt02.cntktest', '2pair4test',  [],  ['1', '0'])
    print '3'
#    get_instance_list_fromSVM('../mt/best_worst_run1/mt05',  '../mt/best_worst_run1/mt05.cntktest', '2pair4test',  [],  ['1', '0'])
 #   get_instance_list_fromSVM('../mt/best_worst_run1/mt06',  '../mt/best_worst_run1/mt06.cntktest', '2pair4test',  [],  ['1', '0'])

