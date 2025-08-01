# matching/similarity.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def rank_jobs_by_keyword(df, user_keyword):
    if df.empty or 'text_for_matching' not in df.columns:
        print("数据为空或缺少'text_for_matching'列，无法进行排序。")
        return pd.DataFrame()
    corpus = [str(user_keyword)] + df['text_for_matching'].astype(str).tolist()
    print("正在计算TF-IDF向量...")
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        print("TF-IDF计算失败，可能是语料库为空。")
        return df
    print("正在计算余弦相似度...")
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    df['similarity_score'] = cosine_sim.flatten()
    sorted_df = df.sort_values(by='similarity_score', ascending=False).reset_index(drop=True)
    print("职位排序完成。")
    return sorted_df