import nltk
from nltk.corpus import wordnet
import re
from typing import List, Tuple

# Download required NLTK data
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def get_food_related_synsets() -> list:
    """Get all synsets related to food and beverages."""
    food_synsets = []
    
    # Main food categories
    food_categories = [
        'food.n.01',  # food
        'beverage.n.01',  # drink
        'meal.n.01',  # meal
        'dish.n.02',  # dish
        'cuisine.n.01',  # cuisine
        'restaurant.n.01',  # restaurant
        'cooking.n.01',  # cooking
        'ingredient.n.01',  # ingredient
        'spice.n.01',  # spice
        'fruit.n.01',  # fruit
        'vegetable.n.01',  # vegetable
        'meat.n.01',  # meat
        'seafood.n.01',  # seafood
        'dessert.n.01',  # dessert
        'snack.n.01',  # snack
    ]
    
    for category in food_categories:
        try:
            synset = wordnet.synset(category)
            food_synsets.append(synset)
            # Add hyponyms (more specific terms)
            food_synsets.extend(synset.hyponyms())
        except nltk.corpus.reader.wordnet.WordNetError:
            continue
    
    return food_synsets

def get_food_related_words() -> set:
    """Get a set of all food-related words from WordNet and common terms."""
    food_words = set()
    food_synsets = get_food_related_synsets()
    
    for synset in food_synsets:
        # Add the lemma names (word forms)
        food_words.update(synset.lemma_names())
        
        # Add related words
        for hypernym in synset.hypernyms():
            food_words.update(hypernym.lemma_names())
        for hyponym in synset.hyponyms():
            food_words.update(hyponym.lemma_names())
    
    # Add common food-related terms, including multi-word terms
    additional_terms = {
        'food', 'drink', 'eat', 'meal', 'restaurant', 'cafe', 'bistro', 'diner',
        'kitchen', 'cook', 'chef', 'recipe', 'cuisine', 'dining', 'catering',
        'bakery', 'butcher', 'grocery', 'market', 'store', 'shop', 'delicatessen',
        'buffet', 'takeout', 'delivery', 'fastfood', 'fast-food', 'organic',
        'vegan', 'vegetarian', 'gluten', 'dairy', 'meat', 'fish', 'seafood',
        'poultry', 'produce', 'fruit', 'vegetable', 'herb', 'spice', 'seasoning',
        'sauce', 'dressing', 'condiment', 'dessert', 'snack', 'beverage', 'drink',
        'coffee', 'tea', 'juice', 'wine', 'beer', 'liquor', 'spirit', 'cocktail',
        'breakfast', 'lunch', 'dinner', 'supper', 'brunch', 'appetizer', 'entree',
        'main', 'side', 'dish', 'plate', 'bowl', 'utensil', 'cutlery', 'cookware',
        'pantry', 'fridge', 'freezer', 'stove', 'oven', 'grill', 'microwave',
        'cooking', 'baking', 'grilling', 'roasting', 'frying', 'boiling', 'steaming',
        # Multi-word food terms (add both spaced and concatenated forms)
        'apple pie', 'applepie', 'ice cream', 'icecream', 'chocolate cake', 'chocolatecake',
        'pumpkin pie', 'pumpkinpie', 'fried chicken', 'friedchicken', 'mashed potatoes', 'mashedpotatoes',
        'hot dog', 'hotdog', 'hamburger', 'cheeseburger', 'french fries', 'frenchfries',
        'mac and cheese', 'macandcheese', 'peanut butter', 'peanutbutter', 'spaghetti', 'lasagna',
        'pizza', 'sushi', 'taco', 'burrito', 'sandwich', 'salad', 'noodle', 'noodles',
        'pie', 'cake', 'cookie', 'brownie', 'muffin', 'croissant', 'bagel', 'donut',
        'waffle', 'pancake', 'bacon', 'sausage', 'egg', 'omelette', 'toast', 'jam',
        'jelly', 'honey', 'butter', 'cream', 'yogurt', 'milk', 'cheese', 'mozzarella',
        'cheddar', 'parmesan', 'gouda', 'brie', 'feta', 'goat cheese', 'goatcheese',
        'almond', 'cashew', 'peanut', 'walnut', 'pecan', 'hazelnut', 'macadamia',
        'pistachio', 'nut', 'seed', 'sunflower seed', 'sunflowerseed', 'chia seed', 'chiaseed',
        'quinoa', 'rice', 'oat', 'oats', 'barley', 'wheat', 'corn', 'maize', 'rye',
        'lentil', 'bean', 'chickpea', 'pea', 'soy', 'tofu', 'tempeh', 'seitan',
        'broccoli', 'carrot', 'potato', 'tomato', 'onion', 'garlic', 'pepper', 'lettuce',
        'spinach', 'kale', 'cabbage', 'cauliflower', 'zucchini', 'eggplant', 'squash',
        'pumpkin', 'cucumber', 'celery', 'radish', 'turnip', 'parsnip', 'beet', 'leek',
        'asparagus', 'artichoke', 'avocado', 'mushroom', 'olive', 'pickles', 'pickle',
        'apple', 'banana', 'orange', 'lemon', 'lime', 'grapefruit', 'grape', 'pear',
        'peach', 'plum', 'cherry', 'berry', 'strawberry', 'blueberry', 'raspberry',
        'blackberry', 'cranberry', 'watermelon', 'melon', 'cantaloupe', 'honeydew',
        'pineapple', 'mango', 'papaya', 'kiwi', 'pomegranate', 'apricot', 'fig', 'date',
        'coconut', 'guava', 'passionfruit', 'dragonfruit', 'lychee', 'starfruit',
        'persimmon', 'tangerine', 'mandarin', 'nectarine', 'currant', 'gooseberry',
        'mulberry', 'boysenberry', 'elderberry', 'loganberry', 'cloudberry',
    }
    
    # Add both spaced and concatenated forms for multi-word terms
    multi_word_terms = [term for term in additional_terms if ' ' in term]
    for term in multi_word_terms:
        additional_terms.add(term.replace(' ', ''))
    food_words.update(additional_terms)
    return food_words

def check_domain_for_food_terms(domain: str, food_words: set) -> Tuple[bool, List[str]]:
    """
    Check if a domain contains food-related terms as substrings (including concatenated words).
    Returns (is_food_related, list_of_found_terms)
    """
    domain = domain.lower()
    domain = re.sub(r'\.[a-z]+$', '', domain)  # Remove TLD
    domain = re.sub(r'[^a-z0-9]', '', domain)  # Remove all non-alphanumeric chars for substring search
    found_terms = []
    # Sort food words by length (longest first) to prioritize longer matches
    sorted_food_words = sorted(food_words, key=len, reverse=True)
    for word in sorted_food_words:
        word_clean = word.replace('_', '').replace(' ', '').lower()
        if word_clean and word_clean in domain:
            found_terms.append(word)
    return len(found_terms) > 0, found_terms

def analyze_domains(domains: List[str]) -> dict:
    """
    Analyze a list of domains for food-related terms.
    Returns a dictionary with results.
    """
    food_words = get_food_related_words()
    results = {
        'food_related': [],
        'not_food_related': [],
        'found_terms': {}
    }
    
    for domain in domains:
        is_food_related, found_terms = check_domain_for_food_terms(domain, food_words)
        if is_food_related:
            results['food_related'].append(domain)
            results['found_terms'][domain] = found_terms
        else:
            results['not_food_related'].append(domain)
    
    return results

if __name__ == "__main__":
    # Example usage
    test_domains = [
        "foodieheaven.com",
        "techblog.net",
        "restaurantfinder.org",
        "codingacademy.com",
        "coffeeshop.io",
        "bakerydelights.com",
        "applepiehumans.com",
        "icecreamworld.net",
        "peanutbutterlovers.org"
    ]
    
    results = analyze_domains(test_domains)
    
    print("\nFood-related domains:")
    for domain in results['food_related']:
        print(f"- {domain} (terms: {', '.join(results['found_terms'][domain])})")
    
    print("\nNon-food-related domains:")
    for domain in results['not_food_related']:
        print(f"- {domain}") 