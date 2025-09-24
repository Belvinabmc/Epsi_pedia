from core.models.article import Article
from datetime import datetime

class ArticleRepository:
    def __init__(self, update_service):
        self.articles = []
        self.next_id = 1
        self.update_service = update_service

    def add_article(self, title: str, content: str, created_at: datetime) -> Article:
        article = Article(self.next_id, title, content)
        self.articles.append(article)
        self.update_service.log_update(article.id, f"Création de l'article '{title}'")
        self.next_id += 1
        return article
    
    def show_all(self) -> list[Article]:
        return self.articles
    
    def show_by_id(self, article_id: int) -> Article | None:
        for article in self.articles:
            if article.id == article_id:
                return article
        return None
    
    def edit_article(self, article_id: int, title: str = None, content: str = None) -> bool:
        article = self.show_by_id(article_id)
        if article:
            changes = []
            if title and title != article.title:
                changes.append(f"Titre : '{article.title}' -> '{title}'")
                article.title = title
            if content and content != article.content:
                changes.append(f"Contenu : '{article.content}' -> '{content}'")
                article.content = content

            if changes:
                summary = "; ".join(changes)
                self.update_service.log_update(article.id, summary)
            return True
        return False
        
    def delete_article(self, article_id: int) -> bool:
        article = self.show_by_id(article_id)
        if article:
            self.articles.remove(article)
            self.update_service.log_update(article.id, f"Suppression de l'article '{article.title}'")
            return True
        return False

