"""
🧪 Teste do efeito karaoke nas legendas
"""

import os
from subtitle_whisper import transcribe_audio_with_whisper, group_words_into_chunks, create_karaoke_text_image
from PIL import Image

def test_karaoke_effect():
    """Testa criação de imagens com efeito karaoke"""
    print("=" * 60)
    print("🎤 TESTE DO EFEITO KARAOKE")
    print("=" * 60)
    
    # Procura áudio de teste
    output_dir = "assets/output"
    if not os.path.exists(output_dir):
        print("⚠️ Pasta assets/output não existe")
        return False
    
    audio_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
    if not audio_files:
        print("⚠️ Nenhum arquivo de áudio encontrado")
        print("💡 Execute: python main.py")
        return False
    
    audio_file = os.path.join(output_dir, sorted(audio_files)[-1])
    print(f"📁 Usando: {os.path.basename(audio_file)}\n")
    
    # Transcreve
    print("🎙️ Transcrevendo áudio...")
    segments = transcribe_audio_with_whisper(audio_file, model_name="tiny")
    
    if not segments or len(segments) < 4:
        print("❌ Transcrição falhou")
        return False
    
    # Agrupa em chunks
    chunks = group_words_into_chunks(segments, max_words=2)
    
    if not chunks:
        print("❌ Nenhum chunk criado")
        return False
    
    # Pega primeiro chunk
    first_chunk = chunks[0]
    print(f"\n📝 Testando chunk: {' '.join([w['text'] for w in first_chunk['words']])}")
    print(f"   Palavras: {len(first_chunk['words'])}")
    
    # Testa criação de imagens com cada palavra destacada
    test_dir = "assets/output/karaoke_test"
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"\n🎨 Gerando imagens de teste...\n")
    
    for word_index in range(len(first_chunk["words"])):
        word = first_chunk["words"][word_index]["text"]
        
        try:
            # Cria imagem com palavra destacada
            img_array = create_karaoke_text_image(
                first_chunk["words"],
                word_index,
                1080,
                300,
                style="tiktok"
            )
            
            # Salva imagem
            img = Image.fromarray(img_array)
            filename = f"karaoke_palavra_{word_index}_{word}.png"
            filepath = os.path.join(test_dir, filename)
            img.save(filepath)
            
            print(f"   ✅ Palavra {word_index + 1}: '{word}' em AMARELO → {filename}")
            
        except Exception as e:
            print(f"   ❌ Erro na palavra '{word}': {e}")
            return False
    
    print(f"\n🎉 Teste concluído!")
    print(f"📁 Imagens salvas em: {test_dir}")
    print(f"\n💡 Abra as imagens para ver o efeito karaoke:")
    print(f"   - Cada imagem mostra uma palavra diferente em AMARELO")
    print(f"   - As outras palavras ficam em BRANCO")
    print(f"   - No vídeo, isso cria um efeito de 'destaque progressivo'")
    
    return True

if __name__ == "__main__":
    success = test_karaoke_effect()
    
    if success:
        print("\n✨ Sistema de karaoke funcionando!")
        print("🎬 Execute 'python main.py' para gerar vídeo com legendas karaoke")
    else:
        print("\n⚠️ Verifique os erros acima")
