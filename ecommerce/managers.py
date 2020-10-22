from django.db.models import Manager


class CustomCategoryManager(Manager):

    def category_with_3_products(self):
        categories = []
        for category in self.filter(visible=True):
            for sub in category.sub_categories.all():
                if sub.products.count() > 3:
                    categories.append((category, sub.products.all()[0:3]))
        return categories
