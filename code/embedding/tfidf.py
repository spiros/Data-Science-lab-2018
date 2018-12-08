from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer

def tfidf(all_ans, ticket_ques):
    vectoriser = TfidfVectorizer(strip_accents='unicode', lowercase=True, analyzer='word', stop_words='english')
    # create matrix: rows = all ans; cols = TI-IDF weighted word vector
    vectoriser.fit(all_ans)
    dump(vectoriser, 'embedding/models/TF-IFD-ans.joblib')
    # train model on ans too
    # TODO: use this for classification?
    vec2 = TfidfVectorizer(strip_accents='unicode', lowercase=True, analyzer='word', stop_words='english')
    vec2.fit(ticket_ques)
    dump(vec2, 'embedding/models/TF-IFD-ticket-ques.joblib')