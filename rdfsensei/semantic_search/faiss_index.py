
import faiss
import numpy as np
from typing import List, Dict

class FaissIndex:
    def __init__(self, embedding_dim: int, use_gpu: bool = True):
        self.use_gpu = use_gpu
        if self.use_gpu:
            # Initialize GPU resources
            res = faiss.StandardGpuResources()
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.gpu_index = faiss.index_cpu_to_gpu(res, 0, self.index)
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = []

    def build_index(self, embeddings: np.ndarray, metadata: List[Dict]):
        if self.use_gpu:
            self.gpu_index.add(embeddings)
        else:
            self.index.add(embeddings)
        self.metadata.extend(metadata)
        
    def search(self, query_embedding: np.ndarray, top_k: int = 1):
        if self.use_gpu:
            distances, indices = self.gpu_index.search(query_embedding, top_k)
        else:
            distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['distance'] = dist
                results.append(result)
        return results