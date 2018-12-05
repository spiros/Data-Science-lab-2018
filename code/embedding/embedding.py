import pandas as pd
from .preprocessing import *
from gensim.test.utils import get_tmpfile
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pickle
import os
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer


def embedding():

    # Read in the data
    ticket_dat = pd.read_csv('../data/12-04-ticket_dat.csv')
    faq_dat = pd.read_csv('../data/12-04-faq_dat.csv')
    # Replace the NaNs
    ticket_dat.fillna('', inplace=True)
    faq_dat.fillna('', inplace=True)

    # FAQ question
    faq_ques = list(faq_dat.question)
    n_faq_ques = len(faq_ques)
    # FAQ answer
    faq_ans = list(faq_dat.answer_title + " " + faq_dat.answer)
    n_faq_ans = len(faq_ans)
    #ticket question
    ticket_ques = list(ticket_dat.question)
    n_ticket_ques = len(ticket_ques)
    #ticket ans
    ticket_ans = list(ticket_dat.answer)
    n_ticket_ans = len(ticket_ans)

    # Model assumption: same embedding for all
    all_docs = faq_ques + faq_ans + ticket_ques + ticket_ans
    # Model assumption: two different embeddings
    all_ans = faq_ans + ticket_ans

    # create a dictionary storing the cut points for the four datasets so we can re-split them after.
    # use like all_docs[id_dict['faq_ques']] to get all faq questions.
    id_dict = {
        'faq_ques': range(0, n_faq_ques),
        'faq_ans': range(n_faq_ques, n_faq_ques + n_faq_ans),
        'ticket_ques': range(n_faq_ques + n_faq_ans, n_faq_ques + n_faq_ans + n_ticket_ques),
        'ticket_ans': range(n_faq_ques + n_faq_ans + n_ticket_ques, n_faq_ques + n_faq_ans + n_ticket_ques + n_ticket_ans)
    }
    all_docs_sep = {
        'faq_ques': faq_ques,
        'faq_ans': faq_ans,
        'ticket_ques': ticket_ques,
        'ticket_ans': ticket_ans}

    # Need to save this list and id dictionary as a pickle so we can decode IDs when we test things
    with open("embedding/models/doc_data/all_docs.txt", "wb") as fp:
        pickle.dump(all_docs, fp)
    with open("embedding/models/doc_data/id_dict.txt", "wb") as fp:
        pickle.dump(id_dict, fp)
    with open("embedding/models/doc_data/all_docs_sep.pkl", "wb") as fp:
        pickle.dump(all_docs_sep, fp)

    all_docs_prepro = preprocess_docs_fn(all_docs)
    with open("embedding/models/doc_data/all_docs_prepro.txt", "wb") as fp:
        pickle.dump(all_docs_prepro, fp)


    ############################################################################################################
    # Model assumption: word2vec

    # checking if embedding model already exists
    exists = os.path.isfile('embedding/models/word2vec.model')
    if exists:
        print('Word2vec embedding model already existing')
    # Create word embedding model
    else:
        word_path = "embedding/models/word2vec.model"
        word_tempfile = get_tmpfile(word_path)
        print('Training Word2Vec Model')
        word_model = Word2Vec(all_docs_prepro, size=128, window=5, min_count=1, workers=4)
        word_model.save(word_path)

        print('Trained')
    #####################################################################################################
    """   
    # Model assumption: doc2vec

    # checking if embedding model already exists
    exists = os.path.isfile('embedding/models/doc2vec.model')
    if exists:
        print('Doc2vec embedding model already existing')
    # Create Doc2Vec model
    else:
        doc_path = "embedding/models/doc2vec.model"
        doc_tempfile = get_tmpfile(doc_path)
        # DOC2VEC Model. 1 is distributed memory, 0 is distributed bag of words
        MODEL = 1
        print('Training Doc2Vec Model')
        tagged_docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(all_docs_prepro)]
        doc_model = Doc2Vec(tagged_docs, vector_size=128, window=5, min_count=1, workers=4, dm=MODEL)
        doc_model.save(doc_path)
        print('Trained')
    """
        ########################################################################################################
    # Model assumption: TF-IDF

    # initialise model
    # checking if embedding model already exists
    print('Training TF-IDF Model')
    vectoriser = TfidfVectorizer(strip_accents='unicode', lowercase=True, analyzer='word')
    # create matrix: rows = all ans; cols = TI-IDF weighted word vector
    vectoriser.fit(all_ans)
    dump(vectoriser, 'embedding/models/TF-IFD-ans.joblib')
    # train model on ans too
    # TODO: use this for classification?
    vec2 = TfidfVectorizer(strip_accents='unicode', lowercase=True, analyzer='word')
    vec2.fit(ticket_ques)
    dump(vec2, 'embedding/models/TF-IFD-ticket-ques.joblib')
    print('Trained')

if __name__== "__main__":
    embedding()