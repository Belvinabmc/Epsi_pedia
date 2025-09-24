from core.models.category import Category

class CategoryRepository:
    def __init__(self):
        self.categories = []

    def add_category(self, name: str, description: str = "") -> Category | None:
        if self.show_by_name(name):
            print(f"La catégorie '{name}' existe déjà")
            return None
        
        category = Category(name, description)
        self.categories.append(category)
        return category
    
    def show_all(self) -> list[Category]:
        return self.categories
    
    def show_by_name(self, name: str) -> Category | None:
        for cat in self.categories:
            if cat.name == name:
                return cat
        return None

    def edit_category(self, old_name: str, new_name: str = None, new_description: str = None) -> bool:
        category = self.show_by_name(old_name)
        if not category:
            return False
        
        if new_name and new_name != old_name:
            if self.show_by_name(new_name):
                print(f"Impossible de renommer '{old_name}' en '{new_name}', ce nom existe déjà")
                return False
            category.name = new_name

        if new_description is not None:
            category.description = new_description

        return True

    def delete_category(self, name: str) -> bool:
        category = self.show_by_name(name)
        if category:
            self.categories.remove(category)
            return True
        return False