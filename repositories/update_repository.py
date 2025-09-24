from core.models.update import Update

class UpdateRepository:
    def __init__(self):
        self.updates = []

    
def log_update(self, article_id: int, summary: str):
    update = Update(article_id, summary)
    self.updates.append(update)
    return update

def get_updates_by_article_id(self, article_id: int):
    return [u for u in self.updates if u.article_id == article_id]
