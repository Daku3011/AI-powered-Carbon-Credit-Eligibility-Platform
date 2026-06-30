import os
import numpy as np
from typing import List, Tuple
from app.core.config import settings


KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs")


class KnowledgeBase:
    """Simple numpy-based vector store for RAG."""

    def __init__(self):
        self.documents: List[str] = []
        self.sources: List[str] = []
        self.embeddings: np.ndarray = np.array([])
        self._loaded = False

    def _load_documents(self):
        if self._loaded:
            return

        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

        default_docs = [
            {
                "source": "Indian Carbon Market Draft Policy 2023.pdf",
                "content": (
                    "The Indian Carbon Market (ICM) is being established under the "
                    "Carbon Credit Trading Scheme (CCTS) notified by the Bureau of "
                    "Energy Efficiency (BEE). Projects can register under the Clean "
                    "Development Mechanism (CDM) or the new CCTS framework. To register "
                    "a solar PV project, the project developer must prepare a Project "
                    "Design Document (PDD) demonstrating additionality, calculate "
                    "baseline emissions, and submit to the Designated Operational Entity "
                    "(DOE) for validation. The registered entity then monitors and "
                    "reports emission reductions for credit issuance."
                ),
            },
            {
                "source": "Indian Carbon Market Draft Policy 2023.pdf",
                "content": (
                    "Carbon credit prices in India are expected to range from INR "
                    "500 to INR 1500 per tonne of CO2 equivalent (tCO2e) depending "
                    "on the project type and vintage. The Ministry of Environment, "
                    "Forest and Climate Change (MoEFCC) oversees the regulatory "
                    "framework. Sectoral methodologies cover renewable energy, "
                    "energy efficiency, waste management, and afforestation."
                ),
            },
            {
                "source": "BEE Energy Efficiency Guidelines.pdf",
                "content": (
                    "The Bureau of Energy Efficiency (BEE) mandates energy audits "
                    "for designated consumers in sectors including aluminium, cement, "
                    "chlor-alkali, iron and steel, pulp and paper, textiles, and "
                    "railways. Perform, Achieve and Trade (PAT) scheme sets specific "
                    "energy consumption (SEC) targets. Compliance cycle is 3 years. "
                    "Entities exceeding targets earn Energy Saving Certificates (ESCerts) "
                    "tradeable on power exchanges."
                ),
            },
            {
                "source": "CII Carbon Pricing Report 2024.pdf",
                "content": (
                    "Corporate carbon pricing mechanisms include internal carbon pricing "
                    "(ICP), shadow carbon pricing, and carbon fees. Leading Indian "
                    "corporations have adopted ICP ranging from INR 200 to INR 800 "
                    "per tCO2e for investment decision-making. Voluntary carbon markets "
                    "offer offset opportunities through Gold Standard, Verra VCS, and "
                    "ACR registries."
                ),
            },
            {
                "source": "MoEFCC Climate Action Framework.pdf",
                "content": (
                    "India's Nationally Determined Contributions (NDCs) commit to "
                    "reducing emissions intensity of GDP by 45% by 2030 compared to "
                    "2005 levels, and achieving 50% cumulative electric power installed "
                    "capacity from non-fossil fuel sources. The National Action Plan "
                    "on Climate Change (NAPCC) includes 8 national missions including "
                    "National Solar Mission and National Mission for Enhanced Energy "
                    "Efficiency."
                ),
            },
            {
                "source": "Carbon Credit Verification Standards.pdf",
                "content": (
                    "Carbon credit verification follows ISO 14064-3 and ISO 14065 "
                    "standards. Verification bodies must be accredited under IAF or "
                    "national accreditation bodies. Key principles include "
                    "additionality, permanence, leakage avoidance, and conservative "
                    "baseline setting. Audit cycles typically occur annually with "
                    "third-party verification required for credit issuance."
                ),
            },
        ]

        for doc in default_docs:
            self.documents.append(doc["content"])
            self.sources.append(doc["source"])

        self._loaded = True

    def _simple_embed(self, text: str) -> np.ndarray:
        words = text.lower().split()
        vec = np.zeros(256)
        for w in words:
            idx = hash(w) % 256
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def build_index(self):
        self._load_documents()
        if not self.documents:
            return
        embeddings = []
        for doc in self.documents:
            embeddings.append(self._simple_embed(doc))
        self.embeddings = np.array(embeddings)

    def query(self, query_text: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        if self.embeddings.size == 0:
            self.build_index()

        q_emb = self._simple_embed(query_text)
        similarities = np.dot(self.embeddings, q_emb)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.01:
                results.append((self.documents[idx], self.sources[idx], score))
        return results


_knowledge_base = KnowledgeBase()


def query_chatbot(user_query: str) -> dict:
    """
    Process a user query against the knowledge base and generate an answer.
    """
    try:
        results = _knowledge_base.query(user_query, top_k=3)

        if not results:
            return {
                "query": user_query,
                "answer": "I don't have information about that topic in my knowledge base. Please try rephrasing your question about carbon markets, Indian policies, or registration procedures.",
                "sources": [],
            }

        context_parts = []
        source_set = set()
        for doc, source, score in results:
            context_parts.append(doc)
            source_set.add(source)

        context = "\n\n".join(context_parts)
        sources = sorted(source_set)

        if settings.OPENROUTER_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=settings.OPENROUTER_API_KEY,
                )

                prompt = (
                    f"You are an AI Carbon Consultant for Indian organizations. "
                    f"Answer the user's question using ONLY the following context from "
                    f"official carbon market documents. Be specific, helpful, and "
                    f"reference the source documents when relevant.\n\n"
                    f"CONTEXT:\n{context}\n\n"
                    f"USER QUESTION: {user_query}\n\n"
                    f"If the context doesn't contain enough information, say so honestly. "
                    f"Do not fabricate information."
                )

                response = client.chat.completions.create(
                    model=settings.OPENROUTER_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                )
                answer = response.choices[0].message.content.strip()
            except Exception:
                answer = (
                    f"Based on the available knowledge base documents, here is what I can tell you: "
                    f"{context_parts[0][:500]}..."
                )
        else:
            answer = (
                f"Based on the available knowledge base documents, here is what I can tell you: "
                f"{context_parts[0][:500]}..."
            )

        return {
            "query": user_query,
            "answer": answer,
            "sources": sources,
        }

    except Exception as e:
        return {
            "query": user_query,
            "answer": f"An error occurred while processing your query: {str(e)}",
            "sources": [],
        }
