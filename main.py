from fastapi import FastAPI
from pydantic import BaseModel # FastAPI에서 요청이나 응답의 데이터 구조를 검증하고 파싱 
from typing import List
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from search_enging import SimpleRetriever
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'

app = FastAPI()

# 예시 데이터
# 후에 PostgreSQL과 PGVector 또는 FAISS 활용할 예정
documents = [
    "Quantum computing uses quantum bits or qubits.",
    "Qubits can be in superpositions of states.",
    "Classical computers use bits that are either 0 or 1.",
    "Quantum entanglement enables new communication methods."
]

# RAG에 사용되는 Retriever을 간단하게 구현 
retriever = SimpleRetriever(documents)

# GPT-2 모델
# 이미 Local에 존재하는 gpt2 모델 loading
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)
# model.eval()

# Type Hinting을 통해 클라이언트가 보낼 JSON 형식을 지정 
# FastAPI가 자동으로 이 JSON을 파싱해서 Python 객체로 바꿔줌 
class QueryRequest(BaseModel):
    question: str # question의 type 지정 
    # context: List[str]

# Decorator -> /generate 경로에서 post 처리 기능 
# 간단한 대화 형식에서는 대화로, 전문지식을 요구할때는 RAG로 적절히 조화 
@app.post("/generate")
async def generate_response(query: QueryRequest):
  
    top_contexts = []
    question = query.question
  
    # 질문이 너무 짧거나 일반적인 경우는 Retriever 건너뜀
    if len(question.split()) > 3:
        top_contexts = retriever.search(question, top_k=2)
        prompt = question + "\n\n" + "\n".join(top_contexts)
    else:
        prompt = question
    
    # GPT Tokenizer(BPE)를 통해 prompt 토큰화 -> tensor로 변환
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}  # 장치 동일
    outputs = model.generate(
        **inputs,
        max_new_tokens=150, # 새롭게 생성할 최대 토큰 수 
        do_sample=True, # 샘플링
        temperature=0.7, # 샘플링 무작위성,  1보다 작게하여 덜 무작위하게 
        top_k=50, # 확률이 높은 50개의 단어만 샘플링 후보로 
        top_p=0.95,  #확률 95% 이상 단어 집합 
        eos_token_id = tokenizer.eos_token_id # GPT-2 모델은 eos_token_id를 지정해주면 좋음 
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True) # cls, pad와 같은 special tokens 포함 
    return {'answer':answer,
            'used_contexts':top_contexts}



