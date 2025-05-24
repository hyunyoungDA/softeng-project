from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 간단한 Retriever 구현 
class SimpleRetriever:
    def __init__(self, documents: list[str]):
        self.documents = documents
        self.vectorizer = TfidfVectorizer() # TFIDF 벡터라이저  
        # doc_vectors: 각 document에 대해 TF/IDF를 계산한 값 
        self.doc_vectors = self.vectorizer.fit_transform(documents) 

    # 상위 rating 3개의 document만 retriever
    def search(self, query: str, top_k: int = 3) -> list[str]:
        # 입력한 query 또한 TF/IDF 계산산
        query_vec = self.vectorizer.transform([query])
        # 코사인 유사도를 통해 query와 document 간의 유사도 계산한 후 평탄화 
        similarities = cosine_similarity(query_vec, self.doc_vectors).flatten()
        # argsort를 통해 역순 정렬 밑 top_k 개만 top_indices에 저장 
        top_indices = similarities.argsort()[::-1][:top_k]
        return [self.documents[i] for i in top_indices]
