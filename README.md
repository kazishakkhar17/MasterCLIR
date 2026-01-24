````md
# Cross-Lingual Information Retrieval (CLIR) System  
**Bangla–English News Retrieval**

This repository contains the implementation of a **technology-focused Cross-Lingual Information Retrieval (CLIR) system** designed to retrieve Bangla and English news articles using a combination of **lexical**, **string-similarity**, and **neural semantic** retrieval methods. The core contribution of this project is a **hybrid ranking framework** that fuses heterogeneous retrieval signals into a unified scoring pipeline.

---

## 🔗 Links

- **GitHub Repository:**  
  https://github.com/kazishakkhar17/MasterCLIR.git

- **Live Deployed App (Hugging Face Spaces):**  
  https://huggingface.co/spaces/rgb95/CLIR

---

## 🧩 Problem Scope

Cross-lingual retrieval suffers from:
- Vocabulary mismatch across languages
- Morphological and spelling variations
- Semantic drift in neural embeddings

This system addresses these challenges by **combining sparse, fuzzy, and dense retrieval models** rather than relying on a single paradigm.

---

## 🏗️ System Architecture Overview

The retrieval pipeline consists of four major components:

1. **BM25 Retriever (Lexical)**
2. **Fuzzy Retriever (String Similarity)**
3. **Semantic Retriever (Neural / LaBSE)**
4. **Hybrid Ranker (Score Fusion Layer)**

Each component operates independently, and their outputs are fused at the ranking stage.

---

## 🔍 Model 1: BM25 Retriever (Lexical Search)

- Library: `rank-bm25`
- Retrieval Type: Sparse vector / keyword-based
- Scoring: Term Frequency–Inverse Document Frequency (TF–IDF)

### Role in the System
- Ensures high precision for queries with exact keyword overlap
- Acts as a fallback when semantic models fail due to unseen entities

### Limitation
- Cannot handle synonymy or cross-lingual semantic variation

---

## ✏️ Model 2: Fuzzy Retriever (String Similarity)

- Libraries:
  - `fuzzywuzzy`
  - `python-Levenshtein`
- Similarity Metric: `token_set_ratio`

### Role in the System
- Handles spelling errors, transliteration issues, and morphological variants
- Improves robustness for noisy or user-generated queries

### Scoring
Raw fuzzy scores are normalized to the range **[0,1]** before fusion.

---

## 🧠 Model 3: Semantic Retriever (Neural)

- Model: **LaBSE (Language-Agnostic BERT Sentence Embedding)**
- Library: `sentence-transformers`
- Similarity Metric: Cosine similarity
- Framework: PyTorch

### Key Design Choices
- Documents are encoded as dense vectors using LaBSE
- Query and document embeddings lie in a shared multilingual semantic space
- Only the first 500 characters of each document are used to control memory usage

### Performance Consideration
- Document embeddings are **precomputed and cached**
- One-time embedding cost (~30–40 minutes for ~6k documents on GPU)
- No recomputation during inference

---

## 🔗 Model 4: Hybrid Ranker (Score Fusion)

The Hybrid Ranker is the **core innovation layer** of the system.

### Responsibilities
- Normalizes heterogeneous scores from all retrievers
- Merges results using document URLs as unique identifiers
- Computes a final weighted relevance score

---

### Score Normalization

Min–max normalization is applied independently to each model’s output to ensure scale invariance:

```math
s_{norm} = \frac{s - s_{min}}{s_{max} - s_{min}}
````

If all scores from a retriever are identical, normalized scores are set to 1.0 to avoid division-by-zero artifacts.

---

### Weighted Score Fusion

The final hybrid relevance score is computed using a weighted linear combination:

```math
s_{hybrid} = 0.3 \cdot s_{BM25}
           + 0.2 \cdot s_{fuzzy}
           + 0.5 \cdot s_{semantic}
```

#### Design Rationale

* **Semantic weight (0.5):** Anchors ranking on conceptual meaning, essential for cross-lingual retrieval
* **BM25 weight (0.3):** Preserves lexical precision and exact-entity matching
* **Fuzzy weight (0.2):** Adds robustness against spelling and morphological noise

Documents missing from any retriever’s output are assigned a normalized score of zero for that component.

---

## 🔄 End-to-End Retrieval Flow

1. User submits a query (Bangla or English)
2. BM25, Fuzzy, and Semantic retrievers independently fetch top-*N* candidates
3. Raw scores are normalized to a common [0,1] scale
4. Results are merged by unique document URLs
5. Hybrid score is computed using weighted fusion
6. Documents are ranked and top-*k* results are returned

---

## 🛠️ Technology Stack

### Data Acquisition & Parsing

* `requests`
* `BeautifulSoup (bs4)`

### NLP & Retrieval

* `spacy` (English NLP processing)
* `re` (Regex-based Bangla preprocessing)
* `rank-bm25`
* `fuzzywuzzy`
* `python-Levenshtein`
* `sentence-transformers`
* `torch`

### Translation

* `googletrans`

### System Utilities

* `pickle` (model and embedding serialization)

---

## 🔮 Future Extension: Cross-Lingual Topic Modeling

A planned extension involves integrating **cross-lingual topic modeling** into the hybrid ranking pipeline.

### Concept

* Learn shared latent topics across Bangla and English documents using multilingual embeddings
* Represent both queries and documents as topic distributions
* Introduce topic relevance as an additional normalized ranking signal

### Expected Benefits

* Improved recall for abstract or low-overlap queries
* Reduced dependency on surface-level lexical matching
* Greater robustness against semantic drift across languages

---

## 📄 References

* McCarley, J. S., *Should We Translate the Documents or the Queries?*, ACL, 1999
* Feng et al., *Language-agnostic BERT Sentence Embedding*, ACL, 2022
* Robertson et al., *Okapi at TREC-3*, NIST, 1995

---


Project: *Cross-Lingual Information Retrieval : MasterCLIR*

```
```


```