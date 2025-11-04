"""
Gerador de legendas sincronizadas usando Whisper AI
Transcreve o áudio automaticamente e cria legendas estilizadas
"""

import whisper
from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def transcribe_audio_with_whisper(audio_path, model_name="base"):
    """
    Transcreve áudio usando Whisper com timestamps precisos
    
    Args:
        audio_path: Caminho do arquivo de áudio
        model_name: Modelo do Whisper (tiny, base, small, medium, large)
    
    Returns:
        Lista de segmentos com texto e timestamps
    """
    print(f"🎙️ Transcrevendo áudio com Whisper ({model_name})...")
    
    try:
        # Carrega modelo Whisper
        model = whisper.load_model(model_name)
        
        # Transcreve com word-level timestamps
        result = model.transcribe(
            audio_path,
            language="pt",  # Português
            word_timestamps=True
        )
        
        # Extrai palavras com timestamps
        segments = []
        for segment in result["segments"]:
            if "words" in segment:
                for word_info in segment["words"]:
                    segments.append({
                        "text": word_info["word"].strip(),
                        "start": word_info["start"],
                        "end": word_info["end"]
                    })
            else:
                # Fallback se word_timestamps não estiver disponível
                segments.append({
                    "text": segment["text"].strip(),
                    "start": segment["start"],
                    "end": segment["end"]
                })
        
        print(f"✅ {len(segments)} palavras transcritas!")
        return segments
    
    except Exception as e:
        print(f"❌ Erro ao transcrever: {e}")
        return None

def group_words_into_chunks(segments, max_words=2):
    """
    Agrupa palavras em chunks para exibição
    
    Args:
        segments: Lista de palavras com timestamps
        max_words: Máximo de palavras por chunk
    
    Returns:
        Lista de chunks com texto e timestamps de cada palavra
    """
    chunks = []
    current_chunk = []
    
    for i, segment in enumerate(segments):
        current_chunk.append(segment)
        
        # Cria chunk a cada max_words ou no final
        if len(current_chunk) >= max_words or i == len(segments) - 1:
            chunks.append({
                "words": current_chunk.copy(),  # Lista de palavras com timestamps individuais
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["end"]
            })
            
            current_chunk = []
    
    return chunks

def create_karaoke_text_image(words_list, current_word_index, width, height, style="tiktok"):
    """
    Cria imagem com efeito karaoke (palavra atual colorida, resto em branco)
    
    Args:
        words_list: Lista de palavras do chunk
        current_word_index: Índice da palavra que está sendo falada
        width: Largura da imagem
        height: Altura da imagem
        style: Estilo da legenda (tiktok, youtube, minimal, karaoke)
    
    Returns:
        Array numpy da imagem
    """
    # Cria imagem transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Configurações de estilo
    if style == "tiktok":
        fontsize = 90
        stroke_width = 5
        active_color = 'yellow'  # Palavra sendo falada
        inactive_color = 'white'  # Outras palavras
        stroke_color = 'black'
    elif style == "youtube":
        fontsize = 80
        stroke_width = 4
        active_color = 'yellow'
        inactive_color = 'white'
        stroke_color = 'black'
    elif style == "karaoke":
        fontsize = 85
        stroke_width = 5
        active_color = 'yellow'
        inactive_color = 'white'
        stroke_color = 'black'
    else:  # minimal
        fontsize = 70
        stroke_width = 3
        active_color = (255, 215, 0)  # Dourado
        inactive_color = 'white'
        stroke_color = (50, 50, 50)
    
    # Carrega fonte
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", fontsize)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", fontsize)
        except:
            font = ImageFont.load_default()
    
    # Monta texto completo para calcular centralização
    full_text = " ".join([w["text"] for w in words_list])
    bbox = draw.textbbox((0, 0), full_text, font=font)
    full_width = bbox[2] - bbox[0]
    full_height = bbox[3] - bbox[1]
    
    # Posição inicial centralizada
    start_x = (width - full_width) // 2
    y = (height - full_height) // 2
    
    # Desenha cada palavra com cor apropriada
    current_x = start_x
    
    for i, word_info in enumerate(words_list):
        word = word_info["text"]
        
        # Define cor baseado se é a palavra atual
        if i == current_word_index:
            text_color = active_color
        else:
            text_color = inactive_color
        
        # Desenha contorno (stroke circular)
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                if adj_x*adj_x + adj_y*adj_y <= stroke_width*stroke_width:
                    draw.text((current_x + adj_x, y + adj_y), word, font=font, fill=stroke_color)
        
        # Desenha texto principal
        draw.text((current_x, y), word, font=font, fill=text_color)
        
        # Avança posição X para próxima palavra
        word_bbox = draw.textbbox((0, 0), word + " ", font=font)
        word_width = word_bbox[2] - word_bbox[0]
        current_x += word_width
    
    return np.array(img)

def add_subtitles_to_video(video_clip, audio_path, style="tiktok", position="center", karaoke_mode=True):
    """
    Adiciona legendas sincronizadas ao vídeo usando Whisper
    
    Args:
        video_clip: Clip de vídeo do MoviePy
        audio_path: Caminho do arquivo de áudio
        style: Estilo das legendas (tiktok, youtube, minimal, karaoke)
        position: Posição vertical (center, bottom, top)
        karaoke_mode: Se True, destaca palavra sendo falada em amarelo
    
    Returns:
        VideoClip com legendas
    """
    # Transcreve áudio
    segments = transcribe_audio_with_whisper(audio_path, model_name="base")
    
    if not segments:
        print("⚠️ Falha na transcrição, vídeo sem legendas")
        return video_clip
    
    # Agrupa em chunks
    print(f"📝 Criando legendas {'com efeito karaoke' if karaoke_mode else 'normais'}...")
    chunks = group_words_into_chunks(segments, max_words=2)
    
    # Cria clips de legenda
    subtitle_clips = []
    video_size = video_clip.size
    
    # Define posição Y baseada no parâmetro
    if position == "bottom":
        y_pos = video_size[1] * 0.75
    elif position == "top":
        y_pos = video_size[1] * 0.15
    else:  # center
        y_pos = video_size[1] * 0.50
    
    img_width = int(video_size[0] * 0.95)
    img_height = 300
    
    for chunk in chunks:
        try:
            if karaoke_mode and len(chunk["words"]) > 1:
                # Modo KARAOKE: cria um clip para cada palavra do chunk
                for word_index, word_info in enumerate(chunk["words"]):
                    # Cria imagem com palavra atual destacada
                    text_img = create_karaoke_text_image(
                        chunk["words"],
                        word_index,
                        img_width,
                        img_height,
                        style=style
                    )
                    
                    # Cria clip para essa palavra
                    text_clip = ImageClip(text_img, transparent=True)
                    text_clip = text_clip.set_position(('center', y_pos))
                    text_clip = text_clip.set_start(word_info["start"])
                    text_clip = text_clip.set_duration(word_info["end"] - word_info["start"])
                    
                    subtitle_clips.append(text_clip)
            else:
                # Modo NORMAL: todas as palavras na mesma cor
                # Cria imagem com primeira palavra destacada (simples)
                text_img = create_karaoke_text_image(
                    chunk["words"],
                    0,  # Destaca primeira palavra
                    img_width,
                    img_height,
                    style=style
                )
                
                text_clip = ImageClip(text_img, transparent=True)
                text_clip = text_clip.set_position(('center', y_pos))
                text_clip = text_clip.set_start(chunk["start"])
                text_clip = text_clip.set_duration(chunk["end"] - chunk["start"])
                
                subtitle_clips.append(text_clip)
            
        except Exception as e:
            words_text = " ".join([w["text"] for w in chunk["words"]])
            print(f"⚠️ Erro ao criar legenda '{words_text[:30]}...': {e}")
            continue
    
    print(f"✅ {len(subtitle_clips)} legendas criadas!")
    
    # Compõe vídeo com legendas
    if subtitle_clips:
        final_video = CompositeVideoClip([video_clip] + subtitle_clips)
        return final_video
    else:
        return video_clip

if __name__ == "__main__":
    # Teste
    test_audio = "assets/output/audio_20251103_204222.mp3"
    
    if os.path.exists(test_audio):
        print("🧪 Testando transcrição...")
        segments = transcribe_audio_with_whisper(test_audio, model_name="tiny")
        
        if segments:
            print(f"\n📝 Primeiras palavras transcritas:")
            for seg in segments[:10]:
                print(f"   {seg['start']:.2f}s - {seg['end']:.2f}s: {seg['text']}")
    else:
        print("⚠️ Arquivo de áudio de teste não encontrado")
        print("   Gere um vídeo primeiro com: python main.py")
