"""
Retriever Classes for Module D
Save this as: retrievers.py
"""

from rank_bm25 import BM25Okapi
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np


class BM25Retriever:
    """Lexical retrieval using BM25 algorithm"""
    
    def __init__(self, documents):
        self.documents = documents
        self.corpus = []
        for doc in documents:
            text = (doc.get('title', '') + ' ' + doc.get('body', '')).lower()
            tokens = text.split()
            self.corpus.append(tokens)
        self.bm25 = BM25Okapi(self.corpus)
    
    def search(self, query, top_k=10):
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    'doc': self.documents[idx],
                    'score': float(scores[idx]),
                    'method': 'BM25'
                })
        return results


class FuzzyMatcher:
    """Fuzzy string matching for cross-script queries"""
    
    def __init__(self, documents):
        self.documents = documents
    
    def fuzzy_score(self, query, text):
        return fuzz.token_set_ratio(query.lower(), text.lower()) / 100.0
    
    def search(self, query, top_k=10):
        scores = []
        for doc in self.documents:
            text = doc.get('title', '') + ' ' + doc.get('body', '')[:500]
            score = self.fuzzy_score(query, text)
            scores.append({
                'doc': doc,
                'score': score,
                'method': 'Fuzzy'
            })
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_k]


class SemanticRetriever:
    """Semantic retrieval using multilingual embeddings"""
    
    def __init__(self, documents, model_name='LaBSE'):
        self.documents = documents
        self.model_name = model_name
        self.model = SentenceTransformer('sentence-transformers/LaBSE')
        self.doc_embeddings = None
    
    def search(self, query, top_k=10):
        if self.doc_embeddings is None:
            return []
        
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.doc_embeddings)[0]
        top_indices = torch.argsort(scores, descending=True)[:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'doc': self.documents[idx.item()],
                'score': float(scores[idx]),
                'method': 'Semantic'
            })
        return results


class HybridRanker:
    """Combine multiple retrieval models with weighted scoring"""
    
    def __init__(self, bm25, fuzzy, semantic, weights=(0.3, 0.2, 0.5)):
        self.bm25 = bm25
        self.fuzzy = fuzzy
        self.semantic = semantic
        self.weights = weights
    
    def normalize_scores(self, results):
        if not results:
            return results
        
        scores = [r['score'] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            for r in results:
                r['score'] = 1.0
            return results
        
        for r in results:
            r['score'] = (r['score'] - min_score) / (max_score - min_score)
        return results
    
    def search(self, query, top_k=10):
        # Get results from all models
        bm25_results = self.bm25.search(query, top_k=50)
        fuzzy_results = self.fuzzy.search(query, top_k=50)
        semantic_results = self.semantic.search(query, top_k=50)
        
        # Normalize scores
        bm25_results = self.normalize_scores(bm25_results)
        fuzzy_results = self.normalize_scores(fuzzy_results)
        semantic_results = self.normalize_scores(semantic_results)
        
        # Combine scores by document URL
        combined = {}
        
        for r in bm25_results:
            url = r['doc']['url']
            if url not in combined:
                combined[url] = {
                    'doc': r['doc'],
                    'bm25_score': 0,
                    'fuzzy_score': 0,
                    'semantic_score': 0,
                    'methods': []
                }
            combined[url]['bm25_score'] = r['score']
            combined[url]['methods'].append('BM25')
        
        for r in fuzzy_results:
            url = r['doc']['url']
            if url not in combined:
                combined[url] = {
                    'doc': r['doc'],
                    'bm25_score': 0,
                    'fuzzy_score': 0,
                    'semantic_score': 0,
                    'methods': []
                }
            combined[url]['fuzzy_score'] = r['score']
            combined[url]['methods'].append('Fuzzy')
        
        for r in semantic_results:
            url = r['doc']['url']
            if url not in combined:
                combined[url] = {
                    'doc': r['doc'],
                    'bm25_score': 0,
                    'fuzzy_score': 0,
                    'semantic_score': 0,
                    'methods': []
                }
            combined[url]['semantic_score'] = r['score']
            combined[url]['methods'].append('Semantic')
        
        # Calculate weighted combined score
        for url in combined:
            combined[url]['score'] = (
                combined[url]['bm25_score'] * self.weights[0] +
                combined[url]['fuzzy_score'] * self.weights[1] +
                combined[url]['semantic_score'] * self.weights[2]
            )
            combined[url]['method'] = 'Hybrid'
        
        # Sort by combined score
        final_results = sorted(
            combined.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return final_results[:top_k]