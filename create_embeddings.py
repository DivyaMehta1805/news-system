import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import argparse
from sklearn.metrics.pairwise import cosine_similarity

# List of news topics
NEWS_TOPICS = [
    "Politics", "Economics", "Technology", "Health", "Environment",
    "Education", "Sports", "Entertainment", "Science", "International Affairs",
    "Business", "Crime", "Social Issues", "Culture", "Weather",
    "Finance", "Military", "Religion", "Travel", "Lifestyle"
]

def load_csv(file_path):
    """Load CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)

def prepare_text(df, text_columns):
    """Combine specified text columns into a single string."""
    return df[text_columns].astype(str).agg(' '.join, axis=1)



def get_topic_embeddings(topics, model):
    """Create embeddings for the news topics."""
    return model.encode(topics)

def find_best_matching_topic(article_embedding, topic_embeddings):
    """Find the best matching topic for an article embedding."""
    similarities = cosine_similarity([article_embedding], topic_embeddings)[0]
    best_match_index = np.argmax(similarities)
    return NEWS_TOPICS[best_match_index]


def save_results(df, output_path):
    """Save the DataFrame with embeddings to a CSV file."""
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

def create_embeddings(texts):
    """Create vector embeddings for the given texts."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

def process_articles(df, text_columns, topic_embeddings):
    """Process articles to find best matching topics."""
    text_data = prepare_text(df, text_columns)
    article_embeddings = create_embeddings(text_data)
    
    best_topics = []
    for embedding in article_embeddings:
        best_topic = find_best_matching_topic(embedding, topic_embeddings)
        best_topics.append(best_topic)
    
    df['best_matching_topic'] = best_topics
    return df

def main(input_file, output_file, text_columns):
    """Main function to process the CSV and create embeddings."""
    print(f"Loading CSV file: {input_file}")
    df = load_csv(input_file)
    
    print("Creating embeddings for news topics...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    topic_embeddings = get_topic_embeddings(NEWS_TOPICS, model)
    
    print(f"Processing articles and finding best matching topics...")
    df_with_topics = process_articles(df, text_columns, topic_embeddings)
    
    print(f"Saving results to: {output_file}")
    save_results(df_with_topics, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create vector embeddings for CSV data and find best matching topics.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to save the output CSV file with best matching topics")
    parser.add_argument("text_columns", nargs='+', help="Names of columns to use for creating embeddings")
    
    args = parser.parse_args()
    
    main(args.input_file, args.output_file, args.text_columns)