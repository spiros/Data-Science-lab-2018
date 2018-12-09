from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
import pickle
import numpy as np
from .utils import *
from joblib import dump
from gensim.models import Word2Vec

def all_average(dat, corpus, dct, model_w2v, model_tfidf, id_dict, all_docs_prepro):
    if dat == 'faq_ans':
        ind = id_dict['faq_ans'][0]
        leng = len(id_dict['faq_ans'])
        dat = all_docs_prepro[ind:leng]
    elif dat == 'ticket_ans':
        ind = id_dict['ticket_ans'][0]
        leng = len(id_dict['ticket_ans'])
        dat = all_docs_prepro[ind:leng]
    else:
        ind = id_dict['ticket_ques'][0]
        leng = len(id_dict['ticket_ques'])
        dat = all_docs_prepro[ind:leng]
    mean_ans = np.empty((leng, 128), dtype=float)
    for i in range(leng):
        vector = np.asarray(model_tfidf[corpus[ind]], dtype=float)
        words = np.empty((len(vector), 128), dtype=float)
        for j in range(len(vector)):
            words[j] = model_w2v[dct[int(vector[j,0])]]
        mean_ans[i] = np.average(words, 0, weights=vector[:,1])
        ind += 1
    return mean_ans

def classification(mean_ticket_ques, mapping):
    # RANDOM FOREST CLASSIFIER
    print('RANDOM FOREST CLASSIFIER')
    print('Running CV on Classifier...')
    classifier_CV = RandomForestClassifier()
    cv_score = cross_val_proba_score(classifier_CV, mean_ticket_ques, mapping,
                                     scoring=multilabel_prec, scoring_arg1=1, scoring_arg2=5, n_splits=5)
    #scores = cross_val_score(classifier_CV, mean_ticket_ques, mapping, cv=5)
    #cv_score = scores.mean()
    print('Training Classifier...')
    classifier = RandomForestClassifier()
    classifier.fit(X=mean_ticket_ques, y=mapping)
    y_pred_proba = classifier.predict_proba(mean_ticket_ques)
    dump(classifier, 'classifier/models/RF_word2vec.joblib')
    train_score = multilabel_prec(y=mapping, y_pred_proba=y_pred_proba, what_to_predict=1, nvals=5)
    #train_score = classifier.score(X=mean_ticket_ques, y=mapping)
    print('Training Score: {0} \nCross Val Score: {1}'.format(train_score, cv_score))

    '''
    print('GRADIENT BOOSTING CLASSIEIR')
    print('Running CV on Classifier...')
    Bclassifier_CV = GradientBoostingClassifier()
    scores = cross_val_score(Bclassifier_CV, mean_ticket_ques, mapping, cv=5)
    cv_score = scores.mean()
    print('Training Classifier...')
    Bclassifier = GradientBoostingClassifier()
    Bclassifier.fit(X=mean_ticket_ques, y=mapping)
    # dump(classifier, 'classifier/models/RF_word2vec.joblib')
    train_score = Bclassifier.score(X=mean_ticket_ques, y=mapping)
    print('Training Score: {0} \nCross Val Score: {1}'.format(train_score, cv_score))
    '''

def tfidf_w2v(all_docs_prepro, id_dict):
    with open('../code/similarity/mappings/map_w2v_tfidf_all.pkl', 'rb') as fp:
        Classes = pickle.load(fp)
    mapping = Classes['mapping']

    print('Loading Word2vec model')
    model_path = 'embedding/models/word2vec_all.model'
    model_w2v = Word2Vec.load(model_path)

    print('Loading Word2vec model')
    model_path = 'embedding/models/tfidf_all.model'
    model_tfidf = Word2Vec.load(model_path)

    dat, corpus, dct, model_w2v, model_tfidf, id_dict, all_docs_prepro

    mean_ticket_ques = all_average('ticket_ques', corpus=corpus, dct=dct, model_w2v=model_w2v,
                                   model_tfidf=model_tfidf, id_dict=id_dict, all_docs_prepro=all_docs_prepro)

    classification(mean_ticket_ques, mapping)