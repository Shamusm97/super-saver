import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import re

def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', str(text).lower())

def remove_brand_from_name(name, brand):
    name = str(name).lower()
    brand = str(brand).lower()
    if name.startswith(brand):
        return name[len(brand):].strip()
    return name

def clean_dataset(df):
    df['clean_name'] = df.apply(lambda row: normalize_text(remove_brand_from_name(row['name'], row['brand'])), axis=1)
    df['brand'] = df['brand'].apply(normalize_text)
    return df

def find_similar_products(df1, df2, threshold=0.6):
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
    tfidf_matrix = vectorizer.fit_transform(pd.concat([df1['clean_name'], df2['clean_name']]))
    
    df1_vectors = tfidf_matrix[:len(df1)]
    df2_vectors = tfidf_matrix[len(df1):]
    
    similarities = cosine_similarity(df1_vectors, df2_vectors)
    matches = np.where(similarities > threshold)
    
    return pd.DataFrame({
        'foodstuffs_product': df1.iloc[matches[0]]['name'].values,
        'foodstuffs_brand': df1.iloc[matches[0]]['brand'].values,
        'foodstuffs_productId': df1.iloc[matches[0]]['productId'].values,
        'woolworths_product': df2.iloc[matches[1]]['name'].values,
        'woolworths_brand': df2.iloc[matches[1]]['brand'].values,
        'similarity': similarities[matches]
    })

# Load data
print("Loading data...")
new_world = pd.read_csv('new_world/output.csv')
pak_n_save = pd.read_csv('pak_n_save/output.csv')
woolworths = pd.read_csv('woolworths/output.csv')

# Clean and preprocess New World and Pak n Save data
print("Cleaning and preprocessing New World and Pak n Save data...")
new_world = clean_dataset(new_world)
pak_n_save = clean_dataset(pak_n_save)

# Merge New World and Pak n Save data
print("Merging New World and Pak n Save data...")
foodstuffs = pd.concat([new_world, pak_n_save], ignore_index=True)

# Remove duplicates based on productId
print("Removing duplicates...")
foodstuffs.drop_duplicates(subset=['productId'], keep='first', inplace=True)

# Clean Woolworths data
print("Cleaning Woolworths data...")
woolworths = clean_dataset(woolworths)

# Group products by brand
print("Grouping products by brand...")
foodstuffs_grouped = foodstuffs.groupby('brand')
woolworths_grouped = woolworths.groupby('brand')

# Find similar products
print("Finding similar products...")
all_matches = []

for brand in tqdm(set(foodstuffs['brand']).union(set(woolworths['brand'])), desc="Matching products by brand"):
    foodstuffs_brand = foodstuffs_grouped.get_group(brand) if brand in foodstuffs_grouped.groups else pd.DataFrame()
    woolworths_brand = woolworths_grouped.get_group(brand) if brand in woolworths_grouped.groups else pd.DataFrame()
    
    if not foodstuffs_brand.empty and not woolworths_brand.empty:
        matches = find_similar_products(foodstuffs_brand, woolworths_brand)
        all_matches.append(matches)

# Combine all matches
final_matches = pd.concat(all_matches, ignore_index=True)

# Sort by similarity and get top matches
top_matches = final_matches.sort_values('similarity', ascending=False).head(1000)

# Save results
print("Saving results...")
top_matches.to_csv('product_matches.csv', index=False)

# save all matches
final_matches.to_csv('all_matches.csv', index=False)

print(f"Found {len(final_matches)} matches. Top 1000 saved to 'product_matches.csv'")
