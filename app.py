from transformers import LlamaForCausalLM, LlamaTokenizer

# Load model and tokenizer
model = LlamaForCausalLM.from_pretrained('path_to_llama_model')
tokenizer = LlamaTokenizer.from_pretrained('path_to_llama_model')

def generate_summary(text):
    inputs = tokenizer.encode(text, return_tensors='pt')
    summary_ids = model.generate(inputs, max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

# Example DataFrame with books data
books = pd.DataFrame({
    'title': ['Book1', 'Book2', 'Book3'],
    'genre': ['Sci-Fi', 'Fantasy', 'Romance'],
    'rating': [4.5, 4.0, 3.5]
})

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(books['genre'])

def recommend_books(title, num_recommendations=5):
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(books.index, index=books['title']).drop_duplicates()
    
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    
    book_indices = [i[0] for i in sim_scores]
    return books.iloc[book_indices]

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from models import Book, Review  # Import your SQLAlchemy models

app = FastAPI()

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int
    summary: str

@app.post("/books", response_model=Book)
async def create_book(book: BookCreate):
    async with SessionLocal() as session:
        async with session.begin():
            new_book = Book(**book.dict())
            session.add(new_book)
            await session.commit()
            await session.refresh(new_book)
            return new_book

@app.get("/books")
async def get_books():
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(Book))
            books = result.scalars().all()
            return books

# Additional endpoints for updating, deleting, reviews, and generating summaries


import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_book():
    response = client.post("/books", json={"title": "Book1", "author": "Author1", "genre": "Sci-Fi", "year_published": 2020, "summary": "A great book"})
    assert response.status_code == 200
    assert response.json()["title"] == "Book1"

# Additional tests for other endpoints

# FastAPI generates documentation at /docs and /redoc


from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends

security = HTTPBasic()

@app.post("/books")
async def create_book(book: BookCreate, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "password":
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Proceed with book creation




