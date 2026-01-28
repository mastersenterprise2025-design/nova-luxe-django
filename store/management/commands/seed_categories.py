from django.core.management.base import BaseCommand
from store.models import Category


class Command(BaseCommand):
    help = 'Seed categories with hierarchical structure'

    def handle(self, *args, **options):
        # Clear existing categories
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing categories'))

        # Define category hierarchy
        categories_data = {
            'Footwear': {
                'Men\'s Footwear': ['Casual', 'Formal'],
                'Women\'s Footwear': ['Heels', 'Flats', 'Boots', 'Sports'],
                'Kids\' Footwear': ['School Shoes', 'Sports Shoes', 'Flipflops']
            },
            'Jewellery': {
                None: ['Bangles', 'Payal', 'Necklace']
            },
            'Clothes': {
                'Men\'s Clothing': [],
                'Women\'s Clothing': [],
                'Kids\' Clothing': []
            }
        }

        # Create categories
        created_count = 0

        for main_category, subcategories in categories_data.items():
            # Create main category
            main_cat = Category.objects.create(name=main_category)
            created_count += 1
            self.stdout.write(f'Created main category: {main_category}')

            for sub_parent, sub_cats in subcategories.items():
                if sub_parent is None:
                    # Direct subcategories of main category
                    for sub_cat_name in sub_cats:
                        Category.objects.create(name=sub_cat_name, parent=main_cat)
                        created_count += 1
                        self.stdout.write(f'  Created subcategory: {sub_cat_name}')
                else:
                    # Create parent subcategory first
                    parent_sub_cat = Category.objects.create(name=sub_parent, parent=main_cat)
                    created_count += 1
                    self.stdout.write(f'  Created subcategory: {sub_parent}')

                    # Create child subcategories
                    for child_cat_name in sub_cats:
                        Category.objects.create(name=child_cat_name, parent=parent_sub_cat)
                        created_count += 1
                        self.stdout.write(f'    Created child category: {child_cat_name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} categories!')
        )
