import requests
import os
from dotenv import load_dotenv
from gtts import gTTS
import asyncio
import edge_tts

load_dotenv()

def generate_voice_elevenlabs(text, output_path="assets/output/audio.mp3", voice_id="Rachel"):
    """
    Gera áudio usando ElevenLabs API
    
    Args:
        text: Texto para converter em voz
        output_path: Caminho do arquivo de saída
        voice_id: ID da voz (Rachel, Josh, etc)
    
    Returns:
        Caminho do arquivo gerado
    """
    try:
        api_key = os.getenv("ELEVEN_API_KEY")
        if not api_key:
            raise ValueError("ELEVEN_API_KEY não encontrada no .env")
        
        # Mapeamento de nomes para IDs reais
        voice_map = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Josh": "TxGEqnHWrfWFTfGW9XjX",
            "Bella": "EXAVITQu4vr4xnSDxMaL",
            "Antoni": "ErXwobaYiN019PkySvjV"
        }
        
        voice_id_real = voice_map.get(voice_id, voice_id)
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id_real}"
        
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        print(f"🎙️ Gerando áudio com ElevenLabs (voz: {voice_id})...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"Erro na API: {response.status_code} - {response.text}")
        
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Áudio gerado: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ Erro no ElevenLabs: {e}")
        print("⚠️ Tentando com Google TTS (grátis)...")
        return generate_voice_gtts(text, output_path)

def generate_voice_edge(text, output_path="assets/output/audio.mp3", voice="pt-BR-AntonioNeural", rate="+80%"):
    """
    Gera áudio usando Edge TTS da Microsoft (GRÁTIS!)
    
    Args:
        text: Texto para converter em voz
        output_path: Caminho do arquivo de saída
        voice: Voz a usar (pt-BR-AntonioNeural = masculina, pt-BR-FranciscaNeural = feminina)
        rate: Velocidade (+80% = 1.8x mais rápido)
    
    Returns:
        Caminho do arquivo gerado
    """
    try:
        print(f"🎙️ Gerando áudio com Edge TTS (voz: {voice}, velocidade: {rate})...")
        
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Gera áudio usando Edge TTS (assíncrono)
        async def gerar():
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(output_path)
        
        # Executa função assíncrona
        asyncio.run(gerar())
        
        print(f"✅ Áudio gerado: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ Erro no Edge TTS: {e}")
        print("⚠️ Tentando com Google TTS...")
        return generate_voice_gtts_fallback(text, output_path)

def generate_voice_gtts_fallback(text, output_path="assets/output/audio.mp3", lang="pt-br", slow=False, speed=1.8):
    """
    Gera áudio usando Google TTS (GRÁTIS!)
    
    Args:
        text: Texto para converter em voz
        output_path: Caminho do arquivo de saída
        lang: Idioma (pt-br, en, es, fr, etc)
        slow: Velocidade lenta (False = normal)
        speed: Multiplicador de velocidade (1.8 = 80% mais rápido)
    
    Returns:
        Caminho do arquivo gerado
    """
    try:
        import subprocess
        
        print(f"🎙️ Gerando áudio com Google TTS (idioma: {lang}, velocidade: {speed}x)...")
        
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Gera áudio normal primeiro
        temp_path = output_path.replace(".mp3", "_temp.mp3")
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        # Acelera o áudio usando FFmpeg
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_path,
                '-filter:a', f'atempo={speed}',
                output_path
            ], check=True, capture_output=True)
            
            # Remove arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            # Se FFmpeg falhar, usa o arquivo normal
            print("⚠️ Não foi possível acelerar (FFmpeg não encontrado), usando velocidade normal...")
            if os.path.exists(temp_path):
                os.rename(temp_path, output_path)
        
        print(f"✅ Áudio gerado: {output_path} (velocidade: {speed}x)")
        return output_path
    
    except Exception as e:
        print(f"❌ Erro no Google TTS: {e}")
        return None

def generate_voice(text, output_path="assets/output/audio.mp3", provider="edge", **kwargs):
    """
    Wrapper que escolhe o provider de TTS
    
    Args:
        text: Texto para converter
        output_path: Caminho de saída
        provider: "edge" (Microsoft, grátis), "gtts" (Google, grátis) ou "elevenlabs" (pago)
        **kwargs: Argumentos específicos do provider
    
    Returns:
        Caminho do arquivo gerado
    """
    if provider == "elevenlabs":
        return generate_voice_elevenlabs(text, output_path, kwargs.get("voice_id", "Rachel"))
    elif provider == "edge":
        # Usa Edge TTS (Microsoft) - GRÁTIS com vozes masculinas/femininas!
        voice = kwargs.get("voice", "adam")
        
        # Mapeia nomes amigáveis para vozes Edge
        voice_map = {
            "adam": "pt-BR-AntonioNeural",      # Masculina brasileira
            "antonio": "pt-BR-AntonioNeural",    # Masculina brasileira  
            "francisca": "pt-BR-FranciscaNeural", # Feminina brasileira
            "female": "pt-BR-FranciscaNeural",
            "male": "pt-BR-AntonioNeural"
        }
        
        edge_voice = voice_map.get(voice.lower(), "pt-BR-AntonioNeural")
        rate = kwargs.get("rate", "+80%")  # Velocidade
        
        return generate_voice_edge(text, output_path, edge_voice, rate)
    else:
        # Usa gTTS por padrão (GRÁTIS!)
        return generate_voice_gtts_fallback(
            text, 
            output_path, 
            kwargs.get("lang", "pt-br"), 
            kwargs.get("slow", False),
            kwargs.get("speed", 1.8)
        )

if __name__ == "__main__":
    # Teste
    test_text = "Olá, esta é uma história incrível do Reddit que você precisa ouvir!"
    
    # Testa Google TTS (GRÁTIS!)
    audio = generate_voice(test_text, provider="gtts", lang="pt-br")
    
    if audio:
        print(f"\n🎵 Áudio de teste gerado com sucesso!")
        print(f"📁 Localização: {audio}")
