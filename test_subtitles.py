"""
🧪 Teste do sistema de legendas com Whisper
"""

import os
import sys

def test_whisper_installation():
    """Testa se Whisper está instalado corretamente"""
    print("🔍 Testando instalação do Whisper...")
    
    try:
        import whisper
        print("✅ Whisper instalado com sucesso!")
        
        # Testa se consegue listar modelos
        available_models = whisper.available_models()
        print(f"✅ Modelos disponíveis: {', '.join(available_models)}")
        return True
    
    except ImportError as e:
        print(f"❌ Erro ao importar Whisper: {e}")
        print("💡 Execute: pip install openai-whisper torch torchaudio")
        return False

def test_subtitle_module():
    """Testa se o módulo de legendas funciona"""
    print("\n🔍 Testando módulo subtitle_whisper...")
    
    try:
        from subtitle_whisper import (
            transcribe_audio_with_whisper,
            group_words_into_chunks,
            create_styled_text_image,
            add_subtitles_to_video
        )
        print("✅ Módulo subtitle_whisper importado com sucesso!")
        print("✅ Todas as funções disponíveis:")
        print("   - transcribe_audio_with_whisper()")
        print("   - group_words_into_chunks()")
        print("   - create_styled_text_image()")
        print("   - add_subtitles_to_video()")
        return True
    
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False

def test_image_generation():
    """Testa criação de imagens de legenda"""
    print("\n🔍 Testando geração de imagens de legenda...")
    
    try:
        from subtitle_whisper import create_styled_text_image
        
        # Testa os 3 estilos
        styles = ["tiktok", "youtube", "minimal"]
        
        for style in styles:
            img = create_styled_text_image(
                text="TESTE DE LEGENDA",
                width=1080,
                height=200,
                style=style
            )
            print(f"✅ Estilo '{style}': {img.shape} - OK!")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")
        return False

def test_with_sample_audio():
    """Testa transcrição com áudio existente"""
    print("\n🔍 Testando transcrição com áudio existente...")
    
    # Procura por arquivos de áudio na pasta output
    output_dir = "assets/output"
    
    if not os.path.exists(output_dir):
        print(f"⚠️ Pasta {output_dir} não existe")
        print("💡 Gere um vídeo primeiro com: python main.py")
        return False
    
    # Procura arquivos de áudio
    audio_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
    
    if not audio_files:
        print(f"⚠️ Nenhum arquivo de áudio encontrado em {output_dir}")
        print("💡 Gere um vídeo primeiro com: python main.py")
        return False
    
    # Usa o áudio mais recente
    audio_file = os.path.join(output_dir, sorted(audio_files)[-1])
    print(f"📁 Usando áudio: {audio_file}")
    
    try:
        from subtitle_whisper import transcribe_audio_with_whisper
        
        print("🎙️ Transcrevendo áudio (isso pode demorar ~10 segundos)...")
        segments = transcribe_audio_with_whisper(audio_file, model_name="tiny")
        
        if segments:
            print(f"✅ Transcrição concluída! {len(segments)} palavras detectadas")
            print(f"\n📝 Primeiras 5 palavras:")
            for i, seg in enumerate(segments[:5], 1):
                print(f"   {i}. {seg['start']:.2f}s - {seg['end']:.2f}s: '{seg['text']}'")
            return True
        else:
            print("❌ Transcrição falhou")
            return False
    
    except Exception as e:
        print(f"❌ Erro na transcrição: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA DE LEGENDAS WHISPER AI")
    print("=" * 60)
    
    tests = [
        ("Instalação Whisper", test_whisper_installation),
        ("Módulo de Legendas", test_subtitle_module),
        ("Geração de Imagens", test_image_generation),
        ("Transcrição de Áudio", test_with_sample_audio)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 SISTEMA PRONTO! Pode usar legendas nos vídeos!")
        print("💡 Execute: python main.py")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
        
        if not results[0][1]:  # Whisper não instalado
            print("💡 Instale o Whisper: pip install openai-whisper torch torchaudio")

if __name__ == "__main__":
    main()
