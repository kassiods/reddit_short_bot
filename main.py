"""
🤖 Reddit Shorts Bot - Automação Completa
Gera vídeos curtos automaticamente a partir de histórias do Reddit
"""

import os
from datetime import datetime
from reddit_fetch import get_story_from_multiple_subs
from summarize import summarize_text, generate_title_and_hashtags
from tts_generate import generate_voice
from video_generate import create_video

def main():
    """Executa o fluxo completo de geração do vídeo"""
    
    print("=" * 60)
    print("🤖 REDDIT SHORTS BOT - INICIANDO...")
    print("=" * 60)
    
    # ETAPA 1: Buscar história do Reddit
    print("\n📖 [1/5] Buscando história no Reddit...")
    story = get_story_from_multiple_subs()
    
    if not story:
        print("❌ Falha ao buscar história. Encerrando.")
        return
    
    print(f"✅ História encontrada!")
    print(f"   📌 Subreddit: r/{story['subreddit']}")
    print(f"   ⭐ Score: {story['score']}")
    print(f"   📝 Título: {story['title'][:80]}...")
    
    # ETAPA 2: Resumir e adaptar o texto
    print("\n✍️ [2/5] Adaptando texto para formato de vídeo...")
    adapted_text = summarize_text(story['title'], story['text'], max_duration=60)
    
    if not adapted_text:
        print("❌ Falha ao adaptar texto. Encerrando.")
        return
    
    print(f"✅ Texto adaptado ({len(adapted_text.split())} palavras)")
    print(f"   Prévia: {adapted_text[:150]}...")
    
    # ETAPA 3: Gerar título e hashtags
    print("\n🏷️ [3/5] Gerando título e hashtags...")
    metadata = generate_title_and_hashtags(adapted_text)
    
    print(f"✅ Metadados gerados:")
    print(f"   📌 Título: {metadata['title']}")
    print(f"   🏷️ Hashtags: {', '.join(metadata['hashtags'][:5])}")
    
    # ETAPA 4: Gerar áudio com IA
    print("\n🎙️ [4/5] Gerando narração com IA...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = f"assets/output/audio_{timestamp}.mp3"
    
    # Escolhe provider (Edge TTS = VOZ MASCULINA GRÁTIS!)
    audio_file = generate_voice(
        adapted_text,
        output_path=audio_path,
        provider="edge",  # Edge TTS da Microsoft - GRÁTIS!
        voice="adam",  # Voz masculina brasileira (Antonio)
        rate="+80%"  # Velocidade 1.8x (mais dinâmico para Shorts)
    )
    
    if not audio_file:
        print("❌ Falha ao gerar áudio. Encerrando.")
        return
    
    # ETAPA 5: Criar vídeo final
    print("\n🎬 [5/5] Montando vídeo final...")
    
    video_path = f"assets/output/video_{timestamp}.mp4"
    final_video = create_video(
        audio_path=audio_file,
        output_path=video_path,
        background_dir="assets/videos/",
        videos_count=3,  # Usa 3 vídeos diferentes!
        add_subtitles=True,  # Ativa legendas com Whisper
        subtitle_style="tiktok"  # Estilo: tiktok, youtube ou minimal
    )
    
    if not final_video:
        print("❌ Falha ao gerar vídeo. Encerrando.")
        return
    
    # SUCESSO!
    print("\n" + "=" * 60)
    print("🎉 VÍDEO GERADO COM SUCESSO!")
    print("=" * 60)
    print(f"\n📁 Localização: {final_video}")
    print(f"📌 Título sugerido: {metadata['title']}")
    print(f"🏷️ Hashtags: #{' #'.join(metadata['hashtags'][:8])}")
    print(f"\n💡 Próximos passos:")
    print(f"   1. Assista o vídeo em: {os.path.abspath(final_video)}")
    print(f"   2. Faça upload no YouTube Shorts / TikTok")
    print(f"   3. Use o título e hashtags gerados acima")
    print("\n✨ Rode novamente para gerar mais vídeos!")

def batch_generate(count=5):
    """
    Gera múltiplos vídeos em sequência
    
    Args:
        count: Quantidade de vídeos para gerar
    """
    print(f"🔄 Modo BATCH: Gerando {count} vídeos...")
    
    for i in range(count):
        print(f"\n{'='*60}")
        print(f"📹 VÍDEO {i+1}/{count}")
        print(f"{'='*60}")
        
        try:
            main()
        except Exception as e:
            print(f"❌ Erro no vídeo {i+1}: {e}")
            continue
    
    print(f"\n✅ Processo batch concluído! {count} vídeos gerados.")

if __name__ == "__main__":
    import sys
    
    # Verifica se foi passado argumento para batch
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        batch_generate(int(sys.argv[1]))
    else:
        main()
