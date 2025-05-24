import gradio as gr
import requests

# FastAPI 백엔드에 질문 보내고 답변 받는 함수
def query_perplexity(question):
    url = "http://127.0.0.1:8000/generate"
    payload = {
        "question": question,
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("answer", "답변이 없습니다.")
        else:
            return f"Error: {response.status_code} 서버 에러 발생"
    except Exception as e:
        return f"Exception 발생: {str(e)}"

# Gradio 인터페이스 설정
iface = gr.Interface(
    fn=query_perplexity,
    inputs=gr.Textbox(lines=2, placeholder="질문을 입력하세요..."),
    outputs="text",
    title="Perplexity 검색 엔진 데모",
    description="질문을 입력하면 GPT-2 기반 백엔드가 답변을 반환합니다."
)

if __name__ == "__main__":
    iface.launch()
