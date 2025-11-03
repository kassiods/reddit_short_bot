from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def init_groq():
    """Inicializa cliente Groq (GRÁTIS!)"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY não encontrada no .env")
    return Groq(api_key=api_key)

def summarize_text(title, text, max_duration=60):
    """
    Resume e adapta texto para formato de vídeo curto
    
    Args:
        title: Título da história
        text: Texto completo
        max_duration: Duração máxima em segundos (~150 palavras/minuto)
    
    Returns:
        Texto resumido e adaptado
    """
    try:
        client = init_groq()
        
        # Calcula palavras máximas baseado na duração
        max_words = int((max_duration / 60) * 150)
        
        prompt = f"""
Você é um roteirista especializado em vídeos curtos do Reddit.

TAREFA: Adapte a história abaixo para um vídeo de {max_duration} segundos (~{max_words} palavras).

REGRAS:
1. Comece com um GANCHO impactante nos primeiros 3 segundos
2. Use linguagem coloquial e natural (como se estivesse contando para um amigo)
3. Mantenha o suspense e tensão da história original
4. Termine com um final impactante ou pergunta provocativa
5. NÃO use emojis ou markdown
6. Use frases curtas e diretas
7. Foque no conflito principal

HISTÓRIA ORIGINAL:
Título: {title}

{text}

NARRAÇÃO ADAPTADA:
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modelo grátis e poderoso!
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        
        adapted_text = response.choices[0].message.content.strip()
        
        # Remove possíveis aspas no início/fim
        adapted_text = adapted_text.strip('"').strip("'")
        
        return adapted_text
    
    except Exception as e:
        print(f"❌ Erro ao resumir texto: {e}")
        return None

def generate_title_and_hashtags(story_text):
    """
    Gera título chamativo e hashtags para o vídeo
    
    Args:
        story_text: Texto da história
    
    Returns:
        Dict com título e lista de hashtags
    """
    try:
        client = init_groq()
        
        prompt = f"""
Baseado nesta história do Reddit, gere:

1. UM título chamativo para YouTube Shorts (máx 60 caracteres)
2. 5-8 hashtags relevantes (sem #, apenas palavras)

História: {story_text[:500]}

Formato da resposta:
TÍTULO: [título aqui]
HASHTAGS: tag1, tag2, tag3, tag4, tag5
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse da resposta
        lines = result.split('\n')
        title = ""
        hashtags = []
        
        for line in lines:
            if line.startswith("TÍTULO:"):
                title = line.replace("TÍTULO:", "").strip()
            elif line.startswith("HASHTAGS:"):
                tags = line.replace("HASHTAGS:", "").strip()
                hashtags = [tag.strip() for tag in tags.split(',')]
        
        return {
            "title": title,
            "hashtags": hashtags
        }
    
    except Exception as e:
        print(f"❌ Erro ao gerar título/hashtags: {e}")
        return {"title": "História do Reddit", "hashtags": ["reddit", "stories"]}

if __name__ == "__main__":
    # Teste
    test_title = "AITA for telling my sister she can't bring her kids to my wedding?"
    test_text = "So I'm getting married next month..."
    
    summary = summarize_text(test_title, test_text)
    if summary:
        print("📝 Resumo:", summary)
        
        metadata = generate_title_and_hashtags(summary)
        print(f"\n📌 Título: {metadata['title']}")
        print(f"🏷️ Hashtags: {', '.join(metadata['hashtags'])}")
