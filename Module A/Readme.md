# CLIR Project - Module A: Dataset Construction & Indexing

## Dataset Overview

### Statistics
- **Total Documents**: 6,188
- **Bangla Documents**: 3,094 (from Prothom Alo)
- **English Documents**: 3,094 (from The Daily Star)
- **Unique Indexed Terms**: ~45,000+

### Data Sources
| Language | Source | URL |
|----------|--------|-----|
| Bangla | Prothom Alo | prothomalo.com |
| English | The Daily Star | thedailystar.net |

### Metadata Structure
Each document contains:
- `title`: Article headline
- `body`: Full article text
- `url`: Source URL
- `date`: Publication date
- `language`: 'bn' (Bangla) or 'en' (English)
- `source`: News source name
- `word_count`: Number of words
- `tokens`: Token count
- `named_entities`: Extracted named entities (people, places, organizations)

## Implementation Details

### 1. Named Entity Recognition (NER)
- **English NER**: SpaCy (`en_core_web_sm`)
- **Bangla NER**: Stanza (Stanford NLP Bangla model)
- Extracted entities include: persons, locations, organizations

### 2. Inverted Index
- **Structure**: Term → List of Document IDs
- **Tokenization**: Simple word-based tokenization with regex
- **Storage**: Pickle format for fast loading

### 3. Tools Used
- Python 3.x
- SpaCy (English NLP)
- Stanza (Bangla NLP)
- Collections (defaultdict for indexing)
- Pickle (serialization)

## File Structure
```
MASTERCLIR/
├── 📂 Active Files
│   ├── {} bangla_articles_with_ner.json          U
│   ├── {} english_articles_with_ner.json         U
│   └── 📄 simple_index.pkl                        U
│
├── 📂 Module A
│   ├── {} bangla_articles_with_ner.json          U
│   ├── {} bangla_articles.json
│   ├── {} english_articles_with_ner.json         U
│   ├── {} english_articles.json
│   ├── 📓 ModuleA_NER.ipynb                       U
│   ├── 📄 Readme.md                               U
│   ├── 📓 scrap+crawl.ipynb
│   ├── 🐍 scrapper.py
│   └── 📄 simple_index.pkl                        U
│
└── 📄 README.md
```

## How to Run

### Step 1: Add Named Entities
```bash
python add_ner.py
```
This will:
- Load original JSON files
- Extract named entities using SpaCy/Stanza
- Save new files with NER data

**Time**: ~30-45 minutes (depending on CPU)

### Step 2: Build Index
```bash
python build_index.py
```
This will:
- Load documents with NER
- Build inverted index
- Save index to `simple_index.pkl`

**Time**: ~2-3 minutes

### Step 3: Test Search
```bash
python test_index.py
```
This will run sample queries and show results.

## Sample Query Results

### Query: "cricket"
- Found: 127 documents
- Top result: "দাম তো ৯ কোটির বেশি, নিয়মিত একাদশে জায়গা মিলবে কি মোস্তাফিজের"

### Query: "নির্বাচন" (election)
- Found: 89 documents
- Top result: "ঢাকা-দিল্লি সম্পর্কে উত্তেজনা, ভারতীয় ভিসা কেন্দ্র আজ চালু থাকবে"

### Query: "Bangladesh"
- Found: 234 documents
- Top result: "Investigative Stories"

## Challenges & Solutions

### Challenge 1: Bangla NER Performance
- **Issue**: Stanza Bangla model is slower than English
- **Solution**: Limit text length to 5000 characters per document

### Challenge 2: Memory Usage
- **Issue**: Loading all documents can consume significant memory
- **Solution**: Store only document snippets (first 500 chars) in index

### Challenge 3: Encoding Issues
- **Issue**: Unicode handling for Bangla text
- **Solution**: Use `encoding='utf-8'` and `ensure_ascii=False` consistently

## Next Steps (Module B)

Module A provides the foundation. Next steps:
1. Implement query translation (English ↔ Bangla)
2. Add cross-lingual named entity mapping
3. Implement semantic retrieval using embeddings
4. Build ranking and scoring mechanisms

## Module A Completion Checklist
- [x] 2,500+ documents per language
- [x] Required metadata (title, body, url, date, language)
- [x] Named entity extraction
- [x] Inverted index implementation
- [x] Index testing and validation
- [x] Documentation