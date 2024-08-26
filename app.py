import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
import random

from summarizer import article_title_get
app = Flask(__name__)
CORS(app)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Global variables
user_item_matrix = {}
article_features = {}
articles_df = None
tfidf_matrix = None
article_title=""
def get_default_recommendations():
    return articles_df.head(10).to_dict('records')

def get_random_articles(limit=10):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    
    query = """
    SELECT title_1, content_1, best_matching_topic
    FROM articles
    GROUP BY best_matching_topic
    ORDER BY RANDOM()
    LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    
    conn.close()
    
    return [{"title_1": row[0], "content_1": row[1]} for row in results]

def get_topic_for_article(article_title):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    
    query = "SELECT best_matching_topic FROM articles WHERE title_1 = ?"
    cursor.execute(query, (article_title,))
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0] if result else ''

def get_topic_recommendations(topic, limit=10):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    
    query = """
    SELECT title_1, content_1
    FROM articles
    WHERE best_matching_topic LIKE ?
    ORDER BY RANDOM()
    LIMIT ?
    """
    
    cursor.execute(query, (f"%{topic}%", limit))
    results = cursor.fetchall()
    
    conn.close()
    
    return [{"title_1": row[0], "content_1": row[1]} for row in results]

def generate_recommendations(user_id, interacted_articles):
    # Convert user_id to int if it's a numeric string, otherwise use it as is
    try:
        user_id_int = int(user_id)
    except ValueError:
        # If user_id is not a number, use a hash function to create a numeric representation
        user_id_int = hash(user_id) % (2**32)  # Limit to 32-bit integer range

    # If interacted_articles is empty or None, return random articles
    if not interacted_articles:
        return get_random_articles(10)

    # Get the topics of interacted articles
    interacted_topics = [get_topic_for_article(article_title) for article_title in interacted_articles]
    
    # Choose a random topic from interacted articles
    if interacted_topics:
        chosen_topic = random.choice(interacted_topics)
    else:
        # If no valid topics found, return random articles
        return get_random_articles(10)

    # Get recommendations based on the chosen topic
    recommendations = get_topic_recommendations(chosen_topic)

    return recommendations

def update_user_item_matrix(user_id, article_title, interaction_type):
    if user_id not in user_item_matrix:
        user_item_matrix[user_id] = {}
    
    if interaction_type == 'view':
        user_item_matrix[user_id][article_title] = user_item_matrix[user_id].get(article_title, 0) + 1
    elif interaction_type == 'like':
        user_item_matrix[user_id][article_title] = user_item_matrix[user_id].get(article_title, 0) + 2

@app.route('/api/get-recommendations', methods=['GET'])
def get_recommendations():
    print("Received request for recommendations")
    user_id = request.args.get('userId')
    
    if not user_id:
        print("Error: User ID is required")
        return jsonify({'error': 'User ID is required'}), 400

    try:
        print(f"Generating recommendations for user {user_id}")
        recommendations = generate_recommendations(user_id, [])
        print("Recommendations generated successfully")
        print(f"Returning {len(recommendations)} recommendations")

        # Ensure recommendations is always a list
        if not isinstance(recommendations, list):
            recommendations = [recommendations]

        # Ensure each recommendation is JSON serializable
        serializable_recommendations = []
        for rec in recommendations:
            serializable_rec = {
                'title_1': str(rec.get('title_1', '')),
                'content_1': str(rec.get('content_1', ''))[:500]  # Limit content length
            }
            serializable_recommendations.append(serializable_rec)

        print(f"Sample recommendation: {serializable_recommendations[0] if serializable_recommendations else 'None'}")
        return jsonify(serializable_recommendations)
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/record-interaction', methods=['POST'])
def record_interaction():
    data = request.json
    user_id = data.get('userId')
    article_title = data.get('articleTitle')
    interaction_type = data.get('interactionType')
    print(user_id + article_title + interaction_type)
    if not all([user_id, article_title, interaction_type]):
        return jsonify({'error': 'Missing required data'}), 400

    try:
        update_user_item_matrix(user_id, article_title, interaction_type)
        new_recommendations = generate_recommendations(user_id, [article_title])
        article_title=article_title
        return jsonify({'status': 'success', 'newRecommendations': new_recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def initialize_data():
    global articles_df, article_features, tfidf_matrix
    articles_df = pd.read_csv('merged_vector_articles.csv')
    articles_df['title_1'] = articles_df['title_1'].fillna('')
    articles_df['content_1'] = articles_df['content_1'].fillna('')
    articles_df['text'] = articles_df['title_1'] + ' ' + articles_df['content_1']
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(articles_df['text'])
    
    article_features = {title: idx for idx, title in enumerate(articles_df['title_1'])}

def get_article_content(article_title):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    
    query = """
    SELECT content_1
    FROM articles
    WHERE title_1 = ?
    LIMIT 1
    """
    
    cursor.execute(query, (article_title,))
    result = cursor.fetchone()
    conn.close()
    print("Connection successful with DB")
    
    if result and result[0]:
        article_text = str(result[0])  # Ensure it's a string
        try:
            summary_response = summarizer(article_text, max_length=200, min_length=100, do_sample=False)
            
            # Safely extract summary text
            if summary_response and len(summary_response) > 0:
                summary = summary_response[0].get('summary_text', article_text[:200] + "...")
            else:
                summary = article_text[:200] + "..."  # Fallback to first 200 characters
                
            print(summary)
            return summary
        except Exception as e:
            print(f"Error in summarization: {e}")
            return article_text[:200] + "..."  # Fallback to first 200 characters
    else:
        return None  # Return None if no content found

@app.route('/api/summary', methods=['GET'])
def summarize_article_route():
    article_title = request.args.get('articleTitle')
    if not article_title:
        return jsonify({'error': 'Article title is required'}), 400

    summary = get_article_content(article_title)
    
    if summary:
        return jsonify({'summary': summary})
    else:
        return jsonify({'error': 'No content found for the given article title'}), 404
        
if __name__ == '__main__':
    initialize_data()
    app.run(debug=True)