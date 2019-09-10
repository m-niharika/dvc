import pickle
import flask
import numpy as np
import scipy.sparse as sparse
import sklearn.metrics as metrics
import pandas as pd
import os
from pandas._libs import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import precision_recall_curve
import conf


app = flask.Flask(__name__)
port = int(os.getenv("PORT", 9999))
model_file = conf.model

with open(model_file, 'rb') as f:
    u = pickle.Unpickler(f)
    u.encoding = 'latin1'
    model = u.load()
 

@app.route('/predict', methods=['POST'])
def predict():
    test_input=flask.request.get_json(force=True)['path']
    df_test = get_df(test_input)

    bag_of_words = CountVectorizer(stop_words='english', max_features=5000)

    test_words = np.array(df_test.text.str.lower().values.astype('U'))
    bag_of_words.fit(test_words)

    tfidf = TfidfTransformer(smooth_idf=False)
    test_words_binary_matrix = bag_of_words.transform(test_words)
    tfidf.fit(test_words_binary_matrix)
    test_words_tfidf_matrix = tfidf.transform(test_words_binary_matrix)
    id_matrix=sparse.csr_matrix(df_test.id.astype(np.int64)).T
    label_matrix = sparse.csr_matrix(df_test.label.astype(np.int64)).T

    matrix = sparse.hstack([id_matrix, label_matrix, test_words_tfidf_matrix], format='csr')

    labels = matrix[:, 1].toarray()
    x = matrix[:, 2:]
    print(matrix)
    predictions_by_class = model.predict_proba(x)
    predictions = predictions_by_class[:, 1]
    precision, recall, thresholds = precision_recall_curve(labels, predictions)
    auc = metrics.auc(recall, precision)
    response = {'prediction': predictions}

    return json.dumps(auc)


def get_df(input):
    df = pd.read_csv(
        input,
        encoding='utf-8',
        header=None,
        delimiter='\t',
        names=['id', 'label', 'text']
    )

    return df

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=port)
	 
	 

