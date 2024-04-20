import os
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from nltk.stem import SnowballStemmer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify

nltk.download('stopwords')
nltk.download('punkt')

app = Flask(__name__)

df_images_data = pd.read_csv("animals_images_data.csv")

df_images_data = df_images_data.drop('page_url', axis=1)
df_images_data.reset_index(inplace=True)
df_images_data.rename(columns={'index': 'image_id'}, inplace=True)

alt_desc_column = df_images_data['alt_text']
alt_desc_list_of_strings = alt_desc_column.tolist()

image_dictionary = df_images_data.set_index('image_id').to_dict()['alt_text']

def preprocess_documents(documents):
    processed_documents = []
    for document in documents:
        document = str(document).lower()
        tokens = word_tokenize(document)
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        stemmer = SnowballStemmer("english")
        tokens = [stemmer.stem(token) for token in tokens]
        tokens = [token.translate(str.maketrans('', '', string.punctuation)) for token in tokens]
        processed_document = " ".join(tokens)
        processed_documents.append(processed_document)
    return processed_documents

def preprocess_query(query):
    query = query.lower()
    tokens = word_tokenize(query)
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    stemmer = SnowballStemmer("english")
    tokens = [stemmer.stem(token) for token in tokens]
    tokens = [token.translate(str.maketrans('', '', string.punctuation)) for token in tokens]
    processed_query = " ".join(tokens)
    return processed_query

processed_documents = preprocess_documents(alt_desc_list_of_strings)
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(processed_documents)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    preprocessed_query = preprocess_query(query)
    query_vector = vectorizer.transform([preprocessed_query])
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix[:-1])
    df = pd.DataFrame(similarity_scores)
    df_transposed = df.transpose().set_axis(['similarity_score'], axis=1)
    df_images_similarity = df_transposed.join(df_images_data)
    filtered = df_images_similarity['similarity_score'] > 0
    df_images_similarity_no_zero = df_images_similarity.loc[filtered]
    df_full_url_sorted_similarity_score_desc = df_images_similarity_no_zero.loc[df_images_similarity_no_zero['similarity_score'].sort_values(ascending=False).index,['image_url','alt_text','similarity_score']]
    df_full_url_sorted_similarity_score_desc['similarity_score'] = df_full_url_sorted_similarity_score_desc['similarity_score'].multiply(100)
    df_full_url_sorted_similarity_score_desc = df_full_url_sorted_similarity_score_desc.reindex(columns=['similarity_score', 'image_url', 'alt_text'])
    df_full_url_sorted_similarity_score_desc['similarity_score'] = df_full_url_sorted_similarity_score_desc['similarity_score'].round(0)
    df_full_url_sorted_similarity_score_desc['similarity_score'] = df_full_url_sorted_similarity_score_desc['similarity_score'].astype(int)
    df_full_url_sorted_similarity_score_desc['similarity_score'] = df_full_url_sorted_similarity_score_desc['similarity_score'].astype(str)
    add_percent = lambda x: str(x) + '%'
    df_full_url_sorted_similarity_score_desc['similarity_score'] = df_full_url_sorted_similarity_score_desc['similarity_score'].apply(add_percent)
    df_full_url_sorted_similarity_score_desc = df_full_url_sorted_similarity_score_desc.rename(columns={'similarity_score': 'similarity'})
    results = df_full_url_sorted_similarity_score_desc.to_dict('records')
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
