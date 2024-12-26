from langchain_core.documents import Document
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from flashrank import Ranker, RerankRequest
from typing import Optional
from pydantic import root_validator

class CustomReranker(BaseDocumentCompressor):
    """Document compressor using Flashrank interface."""

    client: Ranker
    """Flashrank client to use for compressing documents"""
    top_n: int = 3
    """Number of documents to return."""
    model: Optional[str] = None
    """Model to use for reranking."""

    class Config:
        extra = 'forbid'
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def validate_environment(cls, values):
        """Validate that api key and python package exists in environment."""
        try:
            from flashrank import Ranker
        except ImportError:
            raise ImportError(
                "Could not import flashrank python package. "
                "Please install it with `pip install flashrank`."
            )

        values["model"] = values.get("model", "ms-marco-MiniLM-L-12-v2")
        values["client"] = Ranker(model_name=values["model"], cache_dir="reranker")
        return values

    def compress_documents(
        self,
        documents,
        query,
        callbacks = None):
        passages = [
            {"id": i, "text": doc.page_content, "metadata": doc.metadata} for i, doc in enumerate(documents)
        ]
        rerank_request = RerankRequest(query=query, passages=passages)
        rerank_response = self.client.rerank(rerank_request)[:self.top_n]
        final_results = []
        for r in rerank_response:
            doc = Document(
                page_content=r["text"],
                metadata={
                    **r['metadata'],
                    "id": r["id"],
                    "relevance_score": r["score"]
                },
            )
            final_results.append(doc)
        return final_results
