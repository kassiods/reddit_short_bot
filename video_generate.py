try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
    from moviepy.video.fx import crop, resize
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
    from moviepy.video.fx.all import crop, resize
import random
import os

def get_random_backgrounds(videos_dir="assets/videos/", count=3):
    """
    Seleciona múltiplos vídeos de fundo aleatórios
    
    Args:
        videos_dir: Diretório com vídeos de fundo
        count: Quantidade de vídeos para usar
    
    Returns:
        Lista de caminhos dos vídeos escolhidos
    """
    try:
        videos = [f for f in os.listdir(videos_dir) if f.endswith(('.mp4', '.mov', '.avi'))]
        
        if not videos:
            raise Exception(f"Nenhum vídeo encontrado em {videos_dir}")
        
        # Escolhe vídeos aleatórios (pode repetir se não houver suficientes)
        selected = []
        for _ in range(count):
            selected.append(os.path.join(videos_dir, random.choice(videos)))
        
        return selected
    
    except Exception as e:
        print(f"❌ Erro ao buscar vídeos de fundo: {e}")
        return None

def create_vertical_video(video_path, duration):
    """
    Corta vídeo para formato vertical 9:16 (Shorts) e garante duração necessária
    
    Args:
        video_path: Caminho do vídeo
        duration: Duração desejada
    
    Returns:
        VideoClip processado
    """
    from moviepy.editor import concatenate_videoclips
    
    clip = VideoFileClip(video_path)
    original_duration = clip.duration
    
    # Se o vídeo for mais curto que a duração necessária, faz loop manualmente
    if original_duration < duration:
        # Calcula quantas repetições são necessárias
        loops_needed = int(duration / original_duration) + 1
        clips_to_loop = [clip] * loops_needed
        clip = concatenate_videoclips(clips_to_loop)
    
    # Pega segmento do vídeo com duração exata
    if clip.duration > duration:
        start_time = random.uniform(0, max(0, clip.duration - duration))
        clip = clip.subclip(start_time, start_time + duration)
    else:
        # Se ainda for menor (caso raro), ajusta para duração exata
        clip = clip.set_duration(duration)
    
    # Calcula dimensões para 9:16
    target_ratio = 9 / 16
    w, h = clip.size
    current_ratio = w / h
    
    if current_ratio > target_ratio:
        # Vídeo muito largo - crop nas laterais
        new_w = int(h * target_ratio)
        x_center = w / 2
        x1 = int(x_center - new_w / 2)
        clip = clip.crop(x1=x1, width=new_w)
    else:
        # Vídeo muito alto - crop em cima/baixo
        new_h = int(w / target_ratio)
        y_center = h / 2
        y1 = int(y_center - new_h / 2)
        clip = clip.crop(y1=y1, height=new_h)
    
    # Redimensiona para 1080x1920 (resolução padrão do Shorts)
    clip = clip.resize(height=1920)
    
    return clip

def create_video(audio_path, output_path="assets/output/final.mp4", background_dir="assets/videos/", videos_count=3, add_subtitles=True, subtitle_style="tiktok"):
    """
    Cria vídeo final combinando áudio e MÚLTIPLOS vídeos de fundo
    
    Args:
        audio_path: Caminho do arquivo de áudio
        output_path: Caminho de saída do vídeo
        background_dir: Diretório com vídeos de fundo
        videos_count: Quantidade de vídeos diferentes para usar
        add_subtitles: Se True, adiciona legendas com Whisper (padrão: True)
        subtitle_style: Estilo das legendas - tiktok, youtube, minimal (padrão: tiktok)
    
    Returns:
        Caminho do vídeo gerado
    """
    try:
        from moviepy.editor import concatenate_videoclips
        
        print("🎬 Iniciando geração do vídeo...")
        
        # Carrega áudio
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        print(f"⏱️ Duração do áudio: {duration:.1f}s")
        
        # Pega múltiplos vídeos de fundo
        background_paths = get_random_backgrounds(background_dir, videos_count)
        if not background_paths:
            raise Exception("Nenhum vídeo de fundo disponível")
        
        print(f"🎥 Usando {len(background_paths)} vídeos de fundo diferentes")
        
        # Cria clips de cada vídeo
        clips = []
        duration_per_video = duration / videos_count
        
        for i, bg_path in enumerate(background_paths):
            print(f"   📹 Vídeo {i+1}: {os.path.basename(bg_path)}")
            clip = create_vertical_video(bg_path, duration_per_video)
            clips.append(clip)
        
        # Concatena todos os vídeos
        print("🔗 Unindo vídeos...")
        video_clip = concatenate_videoclips(clips, method="compose")
        
        # Garante que o vídeo tenha exatamente a duração do áudio
        if video_clip.duration < duration:
            print(f"⚠️ Ajustando duração do vídeo: {video_clip.duration:.1f}s → {duration:.1f}s")
            video_clip = video_clip.set_duration(duration)
        elif video_clip.duration > duration:
            print(f"⚠️ Cortando vídeo: {video_clip.duration:.1f}s → {duration:.1f}s")
            video_clip = video_clip.subclip(0, duration)
        
        # Adiciona áudio
        final_clip = video_clip.set_audio(audio)
        
        # Adiciona legendas com Whisper se solicitado
        if add_subtitles:
            print("🎙️ Gerando legendas com Whisper AI...")
            try:
                from subtitle_whisper import add_subtitles_to_video
                final_clip = add_subtitles_to_video(
                    final_clip, 
                    audio_path, 
                    style=subtitle_style,
                    position="center",
                    karaoke_mode=True  # Efeito karaoke: palavra atual em amarelo
                )
                print("✅ Legendas sincronizadas adicionadas!")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar legendas: {e}")
                print("   Continuando sem legendas...")
        
        # Cria diretório de saída se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Renderiza vídeo
        print("⚙️ Renderizando vídeo (isso pode demorar)...")
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            threads=4
        )
        
        # Limpa recursos
        audio.close()
        for clip in clips:
            clip.close()
        video_clip.close()
        final_clip.close()
        
        print(f"✅ Vídeo gerado com sucesso: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ Erro ao gerar vídeo: {e}")
        return None

def add_subtitles(video_path, text, output_path):
    """
    [FUTURO] Adiciona legendas ao vídeo
    
    Args:
        video_path: Vídeo de entrada
        text: Texto das legendas
        output_path: Vídeo de saída
    """
    # TODO: Implementar com Whisper ou similar
    pass

if __name__ == "__main__":
    # Teste (precisa de áudio e vídeo de fundo)
    test_audio = "assets/output/audio.mp3"
    
    if os.path.exists(test_audio):
        video = create_video(test_audio, "assets/output/test.mp4")
        if video:
            print(f"\n🎉 Vídeo de teste criado: {video}")
    else:
        print("⚠️ Crie um áudio de teste primeiro usando tts_generate.py")
