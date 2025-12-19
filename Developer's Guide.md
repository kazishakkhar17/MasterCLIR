# MasterCLIR
Cross-Lingual Information Retrieval System (Meta Diners)


```
📋 Handoff: Modules A, B, C Complete → Module D, UI & E
✅ What's Already Done
Module A: Dataset & Indexing

6,188 documents (3,094 Bangla + 3,094 English)
Sources: Prothom Alo, The Daily Star
NER extracted, inverted index built (~40,000 unique terms)
Files: bangla_articles_with_ner.json, english_articles_with_ner.json, simple_index.pkl

Module B: Query Translation

Hybrid translator (Google Translate + M2M100 offline fallback)
21 entities mapped (Bangladesh↔বাংলাদেশ)
Cross-lingual query processing pipeline working
Files: entity_mapper.json, hybrid_translator.py, query_processor.py

Module C: Retrieval Models

4 models: BM25, Fuzzy, Semantic (LaBSE), Hybrid ⭐
Weights: 30% BM25 + 20% Fuzzy + 50% Semantic
All 6,188 documents pre-embedded (768-dim)
Tested on 5 queries, comparison complete
Files: retrieval_system.pkl (~1GB), doc_embeddings.pkl (~800MB), model_comparison.csv


🎯 Your Work: Module D, UI & E
⚠️ CRITICAL: Download First!
📥 Files Location:

Google Drive: [DOWNLOAD LINK] - Get retrieval_system.pkl (~1GB) + doc_embeddings.pkl (~800MB)
GitHub: All other files

Rules:

❌ Don't reload system in loops
❌ Don't rebuild models
✅ Load ONCE at startup with @st.cache_resource
✅ Always use system['hybrid'] for production


🔧 System Integration
Load the System
pythonimport pickle

# Load ONCE at startup
with open('retrieval_system.pkl', 'rb') as f:
    system = pickle.load(f)

# Extract all components
hybrid = system['hybrid']        # ⭐ USE THIS for UI
bm25 = system['bm25']           # For comparison only
semantic = system['semantic']    # For comparison only
fuzzy = system['fuzzy']         # For comparison only
all_docs = system['documents']   # All 6,188 documents
Understanding Results
Each result contains:
pythonresult = {
    'doc': {
        'title': 'Article headline',
        'body': 'Full article text...',
        'url': 'https://...',
        'language': 'en' or 'bn',
        'source': 'The Daily Star' or 'Prothom Alo',
        'date': '2024-12-18',
        'named_entities': ['Bangladesh', 'Dhaka', ...]
    },
    'score': 0.775,              # Combined score (0-1)
    'bm25_score': 0.856,         # Individual model scores
    'fuzzy_score': 0.623,
    'semantic_score': 0.934,
    'methods': ['BM25', 'Semantic']  # Which models contributed
}
Model Selection
Use CaseModelWhyProduction UIhybridBest accuracy + cross-lingualComparisonbm25, semantic, fuzzyShow model differences

📋 Module D: Evaluation
Task 1: Confidence & Timing
pythonimport time

def search_with_metrics(query):
    # Time the search
    start = time.time()
    results = hybrid.search(query, top_k=10)
    elapsed_ms = (time.time() - start) * 1000
    
    # Calculate confidence
    if results:
        top_score = results[0]['score']
        if top_score >= 0.7:
            confidence = "🟢 High"
            warning = None
        elif top_score >= 0.4:
            confidence = "🟡 Medium"
            warning = None
        else:
            confidence = "🔴 Low"
            warning = "⚠️ Low confidence. Try rephrasing your query."
    else:
        confidence = "None"
        warning = "No results found."
    
    return {
        'results': results,
        'time_ms': elapsed_ms,
        'confidence': confidence,
        'warning': warning
    }
Task 2: Evaluation Metrics
Required Metrics:

Precision@10 (≥ 0.6) - Relevant docs in top 10
Recall@50 (≥ 0.5) - Coverage of all relevant docs
nDCG@10 (≥ 0.5) - Ranking quality
MRR (≥ 0.4) - First relevant result position

Create Test Queries:
python# labeled_queries.csv format:
# query,relevant_url_1,relevant_url_2,relevant_url_3

test_queries = [
    {
        'query': 'cricket in Bangladesh',
        'relevant_urls': [
            'https://www.thedailystar.net/sports/cricket/...',
            'https://www.prothomalo.com/sports/cricket/...',
            # ... manually label 3-5 relevant URLs
        ]
    },
    # ... 10-15 more queries (mix Bangla + English)
]
Implement Metrics:
pythondef precision_at_k(results, relevant_urls, k=10):
    top_k = results[:k]
    relevant_found = sum(1 for r in top_k if r['doc']['url'] in relevant_urls)
    return relevant_found / k

def recall_at_k(results, relevant_urls, k=50):
    top_k = results[:k]
    relevant_found = sum(1 for r in top_k if r['doc']['url'] in relevant_urls)
    return relevant_found / len(relevant_urls)

def mrr(results, relevant_urls):
    for i, r in enumerate(results, 1):
        if r['doc']['url'] in relevant_urls:
            return 1.0 / i
    return 0.0

# Run for all test queries
evaluation_results = []
for query_data in test_queries:
    results = hybrid.search(query_data['query'], top_k=50)
    
    eval_result = {
        'query': query_data['query'],
        'precision_at_10': precision_at_k(results, query_data['relevant_urls'], k=10),
        'recall_at_50': recall_at_k(results, query_data['relevant_urls'], k=50),
        'mrr': mrr(results, query_data['relevant_urls'])
    }
    evaluation_results.append(eval_result)

# Calculate averages
avg_p10 = sum(r['precision_at_10'] for r in evaluation_results) / len(evaluation_results)
avg_r50 = sum(r['recall_at_50'] for r in evaluation_results) / len(evaluation_results)
avg_mrr = sum(r['mrr'] for r in evaluation_results) / len(evaluation_results)

print(f"Precision@10: {avg_p10:.3f} (target: ≥0.6)")
print(f"Recall@50: {avg_r50:.3f} (target: ≥0.5)")
print(f"MRR: {avg_mrr:.3f} (target: ≥0.4)")
Task 3: Error Analysis
Analyze 5+ failure cases:

Translation Failures

Query mistranslated → wrong results
Example: "চেয়ার" (chair) → "Chairman" → irrelevant docs


Named Entity Mismatch

"Dhaka" not matching "ঢাকা" in some cases
Show specific example


Semantic vs Lexical

When semantic beats BM25
When BM25 beats semantic
Document differences


Cross-Script Issues

Transliteration problems
"Bangladesh" vs "Bangla Desh"


Code-Switching

Mixed language queries
"cricket এ Bangladesh"



Compare Models:
pythonquery = "education reform"

# Get results from all models
bm25_res = bm25.search(query, top_k=5)
fuzzy_res = fuzzy.search(query, top_k=5)
semantic_res = semantic.search(query, top_k=5)
hybrid_res = hybrid.search(query, top_k=5)

# Document differences
print("BM25 Top 1:", bm25_res[0]['doc']['title'])
print("Fuzzy Top 1:", fuzzy_res[0]['doc']['title'])
print("Semantic Top 1:", semantic_res[0]['doc']['title'])
print("Hybrid Top 1:", hybrid_res[0]['doc']['title'])

# Analyze: Which performed best? Why?
Format: For each case document:

Query text
Expected result
Actual result
Why it failed/succeeded
Screenshot or example

Task 4: Compare with Google/Bing
For same test queries:

Run through your system
Search on Google/Bing
Compare top 10 results
Document precision differences


🖥️ Production UI
Streamlit (Recommended)
pythonimport streamlit as st
import pickle
import time

# Load system ONCE with caching
@st.cache_resource
def load_system():
    with open('retrieval_system.pkl', 'rb') as f:
        return pickle.load(f)

system = load_system()
hybrid = system['hybrid']

# Page config
st.set_page_config(page_title="CLIR System", page_icon="🔍")

# Header
st.title("🔍 Bangla-English CLIR System")
st.caption("Search in English or বাংলা - Get results from both languages")

# Search box
query = st.text_input("🔎 Enter your search query:", 
                      placeholder="e.g., cricket, নির্বাচন, education")

if query:
    # Search with timing
    start = time.time()
    results = hybrid.search(query, top_k=10)
    elapsed = (time.time() - start) * 1000
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Results", len(results))
    col2.metric("⚡ Time", f"{elapsed:.0f}ms")
    
    # Confidence indicator
    if results:
        top_score = results[0]['score']
        if top_score >= 0.7:
            col3.metric("🎯 Confidence", "🟢 High")
        elif top_score >= 0.4:
            col3.metric("🎯 Confidence", "🟡 Medium")
        else:
            col3.metric("🎯 Confidence", "🔴 Low")
            st.warning("⚠️ Low confidence. Results may not be highly relevant. "
                      "Try rephrasing your query.")
    else:
        st.error("❌ No results found. Try different keywords.")
        st.stop()
    
    st.divider()
    
    # Display results
    for i, r in enumerate(results, 1):
        with st.container():
            # Title
            st.markdown(f"### [{i}] {r['doc']['title']}")
            
            # Metadata
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Language:** {r['doc']['language'].upper()}")
            col2.write(f"**Source:** {r['doc']['source']}")
            col3.write(f"**Score:** {r['score']:.3f}")
            
            # Body snippet
            body = r['doc'].get('body', '')[:300]
            st.text(body + "..." if len(body) == 300 else body)
            
            # Model breakdown (collapsible)
            with st.expander("🔍 Model Breakdown"):
                st.write(f"BM25: {r.get('bm25_score', 0):.3f}")
                st.write(f"Fuzzy: {r.get('fuzzy_score', 0):.3f}")
                st.write(f"Semantic: {r.get('semantic_score', 0):.3f}")
            
            # Link
            st.link_button("📖 Read Full Article", r['doc']['url'], 
                          use_container_width=True)
            
            st.divider()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("Cross-lingual search across 6,188 Bangla and English news articles.")
    st.write("**Models:** BM25, Fuzzy, Semantic, Hybrid")
    st.write("**Languages:** বাংলা, English")
Run: streamlit run app.py
Flask Alternative
pythonfrom flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load system at startup
with open('retrieval_system.pkl', 'rb') as f:
    system = pickle.load(f)
hybrid = system['hybrid']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = hybrid.search(query, top_k=10)
    
    # Add confidence
    if results:
        top_score = results[0]['score']
        if top_score >= 0.7:
            confidence = "High"
        elif top_score >= 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
    else:
        confidence = "None"
    
    return render_template('results.html', 
                          query=query, 
                          results=results,
                          confidence=confidence)

if __name__ == '__main__':
    app.run(debug=True)
UI Requirements:

Search box (Bangla + English input)
Results: title, snippet, source, language
Confidence indicator (🟢🟡🔴)
Query time display
Links to full articles
Responsive design


📄 Module E: Report
What You Write:
1. Introduction & Motivation

Problem statement
Why CLIR matters
Project goals

2. Literature Review (3-5 papers)

Cross-lingual IR techniques
Multilingual embeddings (LaBSE, mBERT)
Hybrid ranking methods

3. Methodology

✅ You write: Dataset collection, evaluation approach, UI design
⚠️ Flag for A/B/C: Indexing algorithm details, translator code, model training
Use: <!-- TODO: Get from Module A/B/C -->

4. Results & Analysis

Your evaluation metrics (P@10, R@50, nDCG, MRR)
Comparison with Google/Bing
Error analysis findings
Model comparison charts

5. System Design

Architecture diagram
UI screenshots
User workflow

6. Discussion & Future Work

Strengths & limitations
Potential improvements
Real-world applications

7. AI Usage Log
markdown### Interaction #1
- **Date:** 2024-12-20
- **Prompt:** "How to implement Precision@K in Python?"
- **Tool:** ChatGPT (December 2024)
- **Output:** [code snippet]
- **Verified:** Yes, tested with sample data
- **Used in:** ModuleD_Evaluation.ipynb, cell 15
```

---

## 📊 Expected Deliverables

### **Module D Files:**
```
Module_D/
├── ModuleD_Evaluation.ipynb    ← All metrics & analysis
├── app.py                       ← Streamlit/Flask UI
├── templates/                   ← If using Flask
│   ├── index.html
│   └── results.html
├── labeled_queries.csv          ← 10-15 test queries
├── evaluation_results.json      ← Computed metrics
└── error_analysis.md            ← 5+ documented cases
What Users See (UI):
Search Interface:

Clean search box
Accepts both Bangla and English
Placeholder with examples

Results Display:

Top 10 ranked results
Each shows: title, source, language, snippet, score
Link to full article

Performance Indicators:

Query time (~100ms)
Number of results
Confidence level (High/Medium/Low)
Warning if low confidence

Design:

Responsive (mobile-friendly)
Professional appearance
Fast loading (<2 seconds)

Evaluation Metrics:
json{
  "precision_at_10": 0.67,
  "recall_at_50": 0.53,
  "ndcg_at_10": 0.58,
  "mrr": 0.71,
  "avg_query_time_ms": 103,
  "google_comparison": {
    "google_precision": 0.82,
    "system_precision": 0.67,
    "difference": -0.15
  }
}

🚀 Getting Started
Day 1: Setup
bash# Download files from Drive
# Verify
python3
>>> import pickle
>>> system = pickle.load(open('retrieval_system.pkl', 'rb'))
>>> print(len(system['documents']))  # Should be 6188
>>> results = system['hybrid'].search("test", top_k=3)
>>> print(f"✓ {len(results)} results")

# Install Streamlit
pip install streamlit
streamlit run app.py
```

---

## 📦 Final Submission
```
CLIR_Project_Final/
├── Module_A/           ✅ Complete
├── Module_B/           ✅ Complete
├── Module_C/           ✅ Complete
├── Module_D/           ← YOUR WORK
│   ├── ModuleD_Evaluation.ipynb
│   ├── app.py
│   ├── labeled_queries.csv
│   ├── evaluation_results.json
│   └── error_analysis.md
└── Module_E/           ← YOUR WORK
    ├── Final_Report.pdf
    └── AI_Usage_Log.md

✅ Success Checklist
Module D:

 Confidence levels working
 Query timing measured
 P@10 ≥ 0.6, R@50 ≥ 0.5, nDCG@10 ≥ 0.5, MRR ≥ 0.4
 5+ error cases documented
 Google/Bing comparison done
 UI functional, responsive, <2s load

Module E:

 All 7 sections written
 3-5 papers reviewed
 Unknown sections flagged with <!-- TODO -->
 Results visualized
 UI screenshots included
 AI usage fully documented                                             
 
```