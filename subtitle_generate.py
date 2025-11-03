"""
Gerador de legendas sincronizadas para vídeos
Cria legendas estilo TikTok/Shorts com destaque de palavras
"""

from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import re
import os
import numpy as np

def split_text_into_chunks(text, words_per_chunk=2):
    """
    Divide o texto em chunks de palavras para legendas
    
    Args:
        text: Texto completo
        words_per_chunk: Quantidade de palavras por legenda (2-3 ideal para velocidade 1.8x)
    
    Returns:
        Lista de chunks de texto
    """
    # Remove múltiplos espaços e quebras de linha
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Divide em palavras
    words = text.split()
    
    # Cria chunks de tamanho variável (2-3 palavras)
    chunks = []
    i = 0
    while i < len(words):
        # Alterna entre 2 e 3 palavras para tornar mais natural
        chunk_size = 2 if i % 2 == 0 else 3
        chunk_size = min(chunk_size, len(words) - i)  # Não excede palavras restantes
        
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size
    
    return chunks

def create_subtitle_timings(chunks, total_duration):
    """
    Cria os timings para cada chunk de legenda baseado no número de palavras
    
    Args:
        chunks: Lista de chunks de texto
        total_duration: Duração total do áudio em segundos
    
    Returns:
        Lista de tuplas (start_time, end_time, text)
    """
    if not chunks:
        return []
    
    # Calcula palavras totais
    total_words = sum(len(chunk.split()) for chunk in chunks)
    
    # Tempo por palavra (considerando velocidade 1.8x)
    # Com velocidade 1.8x, aproximadamente 4.5 palavras/segundo
    time_per_word = total_duration / total_words
    
    subtitles = []
    current_time = 0
    
    for chunk in chunks:
        word_count = len(chunk.split())
        duration = word_count * time_per_word
        
        start_time = current_time
        end_time = current_time + duration
        
        subtitles.append((start_time, end_time, chunk))
        current_time = end_time
    
    return subtitles

def create_text_image(txt, width, height, fontsize=80):
    """
    Cria uma imagem com texto usando PIL
    
    Args:
        txt: Texto da legenda
        width: Largura da imagem
        height: Altura da imagem
        fontsize: Tamanho da fonte (maior para melhor legibilidade)
    
    Returns:
        Array numpy da imagem
    """
    # Cria imagem transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Tenta carregar fonte Arial Bold
    try:
        font = ImageFont.truetype("arialbd.ttf", fontsize)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", fontsize)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", fontsize)
            except:
                font = ImageFont.load_default()
    
    # Calcula posição centralizada do texto
    bbox = draw.textbbox((0, 0), txt, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Desenha contorno preto (stroke mais fino)
    stroke_width = 4
    for adj_x in range(-stroke_width, stroke_width + 1):
        for adj_y in range(-stroke_width, stroke_width + 1):
            if adj_x*adj_x + adj_y*adj_y <= stroke_width*stroke_width:
                draw.text((x + adj_x, y + adj_y), txt, font=font, fill='black')
    
    # Desenha texto branco por cima
    draw.text((x, y), txt, font=font, fill='white')
    
    # Converte para array numpy
    return np.array(img)

def create_subtitle_clip(txt, start_time, end_time, video_size):
    """
    Cria um clip de legenda individual com estilo
    
    Args:
        txt: Texto da legenda
        start_time: Tempo de início
        end_time: Tempo de fim
        video_size: Tupla (largura, altura) do vídeo
    
    Returns:
        ImageClip posicionado e estilizado
    """
    # Cria imagem com o texto
    img_width = int(video_size[0] * 0.95)  # 95% da largura
    img_height = 250  # Altura maior para texto maior
    
    text_img = create_text_image(txt, img_width, img_height, fontsize=80)
    
    # Cria clip da imagem
    text_clip = ImageClip(text_img, transparent=True)
    
    # Posiciona no centro (vertical) - melhor para Shorts
    text_clip = text_clip.set_position(('center', video_size[1] * 0.50))
    text_clip = text_clip.set_start(start_time)
    text_clip = text_clip.set_duration(end_time - start_time)
    
    return text_clip

def add_subtitles_to_video(video_clip, text, audio_duration):
    """
    Adiciona legendas ao vídeo
    
    Args:
        video_clip: Clip de vídeo do MoviePy
        text: Texto completo para legendar
        audio_duration: Duração do áudio em segundos
    
    Returns:
        VideoClip com legendas
    """
    # Divide texto em chunks
    chunks = split_text_into_chunks(text, words_per_chunk=3)
    
    # Cria timings
    subtitle_timings = create_subtitle_timings(chunks, audio_duration)
    
    # Cria clips de legenda
    subtitle_clips = []
    video_size = video_clip.size
    
    for start_time, end_time, txt in subtitle_timings:
        try:
            subtitle_clip = create_subtitle_clip(txt, start_time, end_time, video_size)
            subtitle_clips.append(subtitle_clip)
        except Exception as e:
            print(f"⚠️ Erro ao criar legenda '{txt[:30]}...': {e}")
            continue
    
    if not subtitle_clips:
        print("⚠️ Nenhuma legenda foi criada")
        return video_clip
    
    # Compõe vídeo com legendas
    final_video = CompositeVideoClip([video_clip] + subtitle_clips)
    
    return final_video

def generate_srt_file(text, audio_duration, output_path):
    """
    Gera arquivo SRT para legendas (compatível com YouTube)
    
    Args:
        text: Texto completo
        audio_duration: Duração do áudio
        output_path: Caminho para salvar o arquivo .srt
    
    Returns:
        Caminho do arquivo SRT gerado
    """
    chunks = split_text_into_chunks(text, words_per_chunk=3)
    subtitle_timings = create_subtitle_timings(chunks, audio_duration)
    
    # Formato SRT
    srt_content = []
    for i, (start_time, end_time, txt) in enumerate(subtitle_timings, 1):
        # Converte tempo para formato SRT (HH:MM:SS,mmm)
        start_srt = format_time_srt(start_time)
        end_srt = format_time_srt(end_time)
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_srt} --> {end_srt}")
        srt_content.append(txt)
        srt_content.append("")  # Linha em branco
    
    # Salva arquivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))
    
    return output_path

def format_time_srt(seconds):
    """
    Formata tempo em segundos para formato SRT (HH:MM:SS,mmm)
    
    Args:
        seconds: Tempo em segundos (float)
    
    Returns:
        String formatada
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

if __name__ == "__main__":
    # Teste
    test_text = "Imagine você dirigindo em uma noite de Halloween, apenas algumas horas antes da festa, com seu filho no banco de trás, quando de repente você vê um lixo na rua."
    
    chunks = split_text_into_chunks(test_text, words_per_chunk=3)
    print("📝 Chunks de legenda:")
    for i, chunk in enumerate(chunks, 1):
        print(f"   {i}. {chunk}")
    
    print(f"\n✅ Total de {len(chunks)} legendas geradas")
