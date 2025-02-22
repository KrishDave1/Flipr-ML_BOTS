import spacy
from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModel
from neo4j import GraphDatabase
from scipy.spatial.distance import cosine
import numpy as np

# Summarizer starts

from transformers import pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = summarizer.tokenizer
tokenizer.model_max_length = 1024  
MAX_CHUNK_TOKENS = 1200 
MIN_CHUNK_TOKENS = 600
MIN_TOTAL_LAST = 2 * MIN_CHUNK_TOKENS

# Summarizer ends

# NER starts

# Load the pre-trained English NER model
nlp = spacy.load("en_core_web_trf")

# NER ends

app = Flask(__name__)

# HuggingFace Models
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Neo4j Database Connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "valmik_neo4j"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Summarizer helper function

def recursive_summarize(text, min_tokens=MIN_CHUNK_TOKENS, max_tokens=MAX_CHUNK_TOKENS):
    all_tokens = tokenizer.encode(text, add_special_tokens=False)
    total_tokens = len(all_tokens)
    print(f"Total tokens: {total_tokens}")

    if total_tokens <= max_tokens:
        return text
    
    full_chunks = total_tokens // max_tokens
    remainder = total_tokens % max_tokens
    
    if full_chunks >= 1 and remainder < MIN_TOTAL_LAST:
        full_chunks -= 1
        start_last = full_chunks * max_tokens
        last_tokens = all_tokens[start_last:]
    else:
        start_last = full_chunks * max_tokens
        last_tokens = all_tokens[start_last:]

    chunks_tokens = []

    for i in range(full_chunks):
        chunk = all_tokens[i * max_tokens : (i + 1) * max_tokens]
        chunks_tokens.append(chunk)

    last_total = len(last_tokens)
    split_index = last_total // 2

    if split_index < min_tokens or (last_total - split_index) < min_tokens:
        split_index = min_tokens
        if last_total - split_index < min_tokens:
            chunks_tokens.append(last_tokens)
        else:
            chunks_tokens.append(last_tokens[:split_index])
            chunks_tokens.append(last_tokens[split_index:])
    else:
        chunks_tokens.append(last_tokens[:split_index])
        chunks_tokens.append(last_tokens[split_index:])
    
    chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks_tokens]
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        chunk_len = len(tokenizer.encode(chunk, add_special_tokens=False))
        print(f"Chunk {i+1}: {chunk_len} tokens")

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_len = len(tokenizer.encode(chunk, add_special_tokens=False))
        print(f"\nSummarizing chunk {i+1}/{len(chunks)} (token length: {chunk_len})...")
        try:
            summary_chunk = summarizer(
                chunk,
                max_length=600,
                min_length=400,
                do_sample=False,
                truncation=True
            )
            chunk_summaries.append(summary_chunk[0]['summary_text'])
        except Exception as e:
            print(f"Error summarizing chunk {i+1}: {e}")
            chunk_summaries.append(chunk)
    
    combined_summary = " ".join(chunk_summaries)
    print("\nCombined Intermediate Summary:")
    print(combined_summary)

    return recursive_summarize(combined_summary, min_tokens, max_tokens)

def do_ner_and_extract_keywords(text:str) -> list:
    doc = nlp(text)
    keywords =  []
    for ent in doc.ents:
        print(f"{ent.text} -> {ent.label_} ({spacy.explain(ent.label_)})")
        keywords.append(ent.label_)
    return keywords

