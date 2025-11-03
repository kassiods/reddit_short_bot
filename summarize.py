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
        # Para narração em português com velocidade 1.8x: ~250 palavras/minuto
        max_words = int((max_duration / 60) * 250)
        
        prompt = f"""
A partir de agora, você é meu "Roteirista de Impacto". Sua única função é pegar as histórias que eu enviar e transformá-las em roteiros curtos e envolventes, prontos para serem narrados no meu canal de Shorts.

Regras de Adaptação (Obrigatórias):

1. Maximizar o Impacto: Reescreva a história focando nos pontos de virada e emoções. Use uma linguagem que prenda a atenção do ouvinte imediatamente. O objetivo é gerar curiosidade e engajamento.

2. Filtro de Conteúdo (Manter o Sentido): Substitua qualquer conteúdo sensível (gore, cenas sexuais, xingamentos ou linguagem pesada) por versões mais leves. A nova versão deve manter o sentido e a gravidade da cena original.

3. Tom de Voz (Casual): Use sempre o "português do dia a dia". A narração deve soar como um amigo contando uma história. Evite qualquer formalidade.

4. Clareza para Narração: Expanda todas as abreviações para que o texto flua perfeitamente na leitura.
   - Exemplo 1: "M32" deve virar "uma mulher de 32 anos".
   - Exemplo 2: "H40" deve virar "um homem de 40 anos".
   - Exemplo 3: "FDS" deve virar "fim de semana".

5. História Completa: A narração DEVE ter um início, meio e FIM claro. Não deixe a história em aberto ou cortada no meio. Conte a história completa com sua resolução ou conclusão.

6. Estrutura Envolvente:
   - Comece com um GANCHO forte (primeiros 3 segundos são cruciais)
   - Desenvolva o conflito/tensão no meio com DETALHES e CONTEXTO
   - Termine com um FINAL impactante, surpreendente ou que faça o ouvinte refletir

7. Duração OBRIGATÓRIA: Sua narração DEVE ter EXATAMENTE {max_words} palavras (aproximadamente {max_duration} segundos). Isso é CRÍTICO! Não faça textos curtos. Adicione detalhes, contexto, emoções e diálogos para preencher todo o tempo. Se a história original for curta, EXPANDA com detalhes envolventes. Pense em cada segundo do vídeo - use TODO o tempo disponível!

8. NÃO use emojis ou markdown na narração.

Formato de Saída (Obrigatório):
Sua resposta final deve seguir exatamente esta estrutura:

HISTÓRIA ADAPTADA:
[Insira o texto completo da história aqui, já reescrito e adaptado seguindo todas as regras acima.]

HISTÓRIA ORIGINAL:
Título: {title}

{text}
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modelo grátis e poderoso!
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1200  # Aumentado para histórias de 60 segundos (~250 palavras)
        )
        
        full_response = response.choices[0].message.content.strip()
        
        # Extrai apenas a seção "HISTÓRIA ADAPTADA:"
        adapted_text = full_response
        if "HISTÓRIA ADAPTADA:" in full_response:
            # Pega tudo depois de "HISTÓRIA ADAPTADA:"
            parts = full_response.split("HISTÓRIA ADAPTADA:")
            if len(parts) > 1:
                adapted_text = parts[1].strip()
                
                # Remove a seção "HISTÓRIA ORIGINAL:" se existir (apenas essa)
                if "HISTÓRIA ORIGINAL:" in adapted_text:
                    adapted_text = adapted_text.split("HISTÓRIA ORIGINAL:")[0].strip()
        
        # Remove possíveis aspas no início/fim e espaços extras
        adapted_text = adapted_text.strip('"').strip("'").strip()
        
        # Remove linhas em branco múltiplas, mas mantém parágrafos
        adapted_text = "\n".join([line for line in adapted_text.split("\n") if line.strip()])
        
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
