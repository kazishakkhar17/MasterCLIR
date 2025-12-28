import streamlit as st
import pickle
import time
import torch
import io
from retrievers import BM25Retriever, SemanticRetriever, FuzzyMatcher, HybridRanker

# Custom unpickler to handle CUDA->CPU mapping
class CPUUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)

# Load system ONCE with caching
@st.cache_resource
def load_system():
    # Detect device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    with open('Active Files/retrieval_system.pkl', 'rb') as f:
        if torch.cuda.is_available():
            system = pickle.load(f)
        else:
            # Load with CPU mapping
            system = CPUUnpickler(f).load()
    
    # Move models to appropriate device
    if hasattr(system['hybrid'], 'semantic_retriever'):
        semantic = system['hybrid'].semantic_retriever
        if hasattr(semantic, 'model'):
            semantic.model = semantic.model.to(device)
        if hasattr(semantic, 'device'):
            semantic.device = device
    
    # Display device info in sidebar
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'
    st.sidebar.success(f"🖥️ Running on: {device_name}")
    
    return system

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
            st.warning("⚠ Low confidence. Results may not be highly relevant. "
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
    
    st.divider()
    st.caption("💡 Tip: The system automatically uses GPU if available, otherwise runs on CPU.")
