import praw
import random
import os
from dotenv import load_dotenv

load_dotenv()

def init_reddit():
    """Inicializa conexão com Reddit API"""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_SECRET"),
        user_agent="reddit_shorts_bot/1.0"
    )

def get_story(subreddit_name="AmItheAsshole", limit=20, min_length=200):
    """
    Busca uma história aleatória do Reddit
    
    Args:
        subreddit_name: Nome do subreddit
        limit: Quantidade de posts para buscar
        min_length: Tamanho mínimo do texto
    
    Returns:
        Dict com título e texto da história
    """
    try:
        reddit = init_reddit()
        subreddit = reddit.subreddit(subreddit_name)
        
        # Filtra posts válidos (não fixados, com texto suficiente)
        valid_posts = []
        for post in subreddit.hot(limit=limit):
            if not post.stickied and len(post.selftext) >= min_length:
                valid_posts.append(post)
        
        if not valid_posts:
            raise Exception("Nenhuma história válida encontrada")
        
        # Escolhe um post aleatório
        post = random.choice(valid_posts)
        
        return {
            "title": post.title,
            "text": post.selftext[:4000],  # Limita tamanho
            "url": post.url,
            "score": post.score,
            "subreddit": subreddit_name
        }
    
    except Exception as e:
        print(f"❌ Erro ao buscar história: {e}")
        return None

def get_story_from_multiple_subs(subreddits=None, limit=20):
    """
    Busca história de múltiplos subreddits
    
    Args:
        subreddits: Lista de subreddits para buscar
        limit: Posts por subreddit
    
    Returns:
        Dict com história
    """
    if subreddits is None:
        subreddits = [
            "AmItheAsshole",
            "relationship_advice",
            "tifu",
            "confessions",
            "TrueOffMyChest"
        ]
    
    # Escolhe um subreddit aleatório
    chosen_sub = random.choice(subreddits)
    print(f"🔍 Buscando em r/{chosen_sub}...")
    
    return get_story(chosen_sub, limit)

if __name__ == "__main__":
    # Teste
    story = get_story_from_multiple_subs()
    if story:
        print(f"\n📖 Título: {story['title']}")
        print(f"📊 Score: {story['score']}")
        print(f"📝 Texto: {story['text'][:200]}...")
