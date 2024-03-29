import sqlite3
import matplotlib.pyplot as plt

# Establish a connection to the SQLite database
connexion = sqlite3.connect("vivino.db")
cursor = connexion.cursor()

# Fetch top 10 wines to increase sales
cursor.execute("""
    SELECT name, ratings_average AS avg_rating, ratings_count AS rating_count, ratings_average * ratings_count AS rating_product
    FROM vintages
    ORDER BY rating_product DESC
    LIMIT 10;
""")
top_10_wines = cursor.fetchall()

# Write top 10 wines to a text file
with open('top_10_wines.txt', 'w') as f:
    f.write("Top 10 wines to increase sales for Wiwino:\n")
    for wine in top_10_wines:
        f.write(f"Wine: {wine[0]},  Average Rating: {wine[1]}, Rating Count: {wine[2]}, Rating Product: {wine[3]}\n")

# Extract wine names and rating products for plotting
wine_names = [wine[0] for wine in top_10_wines]
rating_products = [wine[3] for wine in top_10_wines]

# Define custom colors for the bars
colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightsteelblue', 
          'lightpink', 'lightseagreen', 'lightgray', 'lightblue', 'lightyellow']

# Create bar chart for top 10 wines to increase sales
plt.figure(figsize=(12, 8))  # Adjust figure size for better readability
bars = plt.barh(wine_names, rating_products, color=colors)

# Add rating product values as text on the bars
for bar, rating in zip(bars, rating_products):
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, str(rating), ha='left', va='center')

plt.xlabel('Rating Product')
plt.ylabel('Wine Name')
plt.title('Top 10 Wines to Increase Sales for Wiwino')
plt.gca().invert_yaxis()  # Invert y-axis to display top-rated wines at the top
plt.tight_layout()  # Adjust layout to fit all text within the plot

# Save the plot as an image
plt.savefig('top_10_wines_plot.png')

# Show the plot
plt.show()

# Top countries to prioritize marketing budget
cursor.execute("""
    SELECT name AS country_name, users_count AS customers
    FROM countries
    ORDER BY users_count DESC
    LIMIT 10;
""")
priority_countries = cursor.fetchall()

# Write top 10 countries to a text file
with open('priority_countries.txt', 'w') as f:
    f.write("Top 10 countries to prioritize marketing budget:\n")
    for country in priority_countries:
        f.write(f"{country}\n")

# Top 3 wines and their corresponding IDs
cursor.execute("""
    SELECT w.id, w.name, w.ratings_average AS avg_rating, w.ratings_count AS rating_count, w.ratings_average * w.ratings_count AS rating_product, c.name AS country_name
    FROM wines AS w
    JOIN regions AS r ON w.region_id = r.id
    JOIN countries AS c ON r.country_code = c.code
    ORDER BY rating_product DESC
    LIMIT 3;
""")
top_3_wines = cursor.fetchall()

# Write top 3 wines to a text file
with open('top_3_wines.txt', 'w') as f:
    f.write("Top 3 wines and their corresponding IDs:\n")
    for wine in top_3_wines:
        wine_id, wine_name, avg_rating, rating_count, rating_product, country_name = wine
        f.write(f"Wine ID: {wine_id}, Name: {wine_name}, Average Rating: {avg_rating}, Rating Count: {rating_count}, Rating Product: {rating_product}, Country: {country_name}\n")

# Extract wine IDs for the subsequent query
wine_ids = [wine[0] for wine in top_3_wines]

# Fetch the names of wineries corresponding to the top 3 wines
winery_names = []
for wine_id in wine_ids:
    cursor.execute("""
        SELECT name
        FROM wineries
        WHERE id = ?;
    """, (wine_id,))
    winery_name = cursor.fetchone()
    if winery_name:
        winery_names.append(winery_name[0])
    else:
        winery_names.append("Unknown")  # Handle the case where the winery ID is not found

# Write names of wineries to a text file
with open('winery_names.txt', 'w') as f:
    f.write("Names of wineries for the award:\n")
    for idx, winery_name in enumerate(winery_names):
        f.write(f"Best wineries {idx + 1}: {winery_name}\n")



# Fetch the group name specific taste keywords
cursor.execute("""
    SELECT id, name
    FROM keywords
    WHERE name LIKE '%coffee%'
        OR name LIKE '%toast%'
        OR name LIKE '%green apple%'
        OR name LIKE '%cream%'
        OR name LIKE '%citrus%'
""")
taste_related_keywords = cursor.fetchall()

# Store unique keywords and their corresponding wine IDs
keyword_wine_mapping = {}
for keyword_id, keyword_name in taste_related_keywords:
    if keyword_id not in keyword_wine_mapping:
        keyword_wine_mapping[keyword_id] = []
    keyword_wine_mapping[keyword_id].append(keyword_name)

# Fetch and store group names corresponding to each wine ID
group_names = {}
for wine_id in keyword_wine_mapping.keys():
    cursor.execute("""
        SELECT keyword_id, group_name
        FROM keywords_wine
        WHERE keyword_id = ?
    """, (wine_id,))
    keyword_group = cursor.fetchone()
    if keyword_group:
        wine_id, group_name = keyword_group
        if group_name not in group_names:
            group_names[group_name] = []
        group_names[group_name].extend(keyword_wine_mapping[wine_id])

# Display the unique group names along with the corresponding keywords
print("\nUnique Group names and their corresponding keywords:")
for group_name, keywords in group_names.items():
    unique_keywords = set(keywords)
    print(f"Group Name: {group_name}")
    print("Keywords:", ", ".join(unique_keywords))

# Write taste-related keywords to a text file
with open('group_taste.txt', 'w') as f:
    f.write("Unique Group names and their corresponding keywords:\n")
    for group_name, keywords in group_names.items():
        f.write(f"Group Name: {group_name}\n")
        f.write("Keywords: " + ", ".join(set(keywords)) + "\n")


# Top 5 grapes per country
cursor.execute("""
    SELECT DISTINCT g.grape_id, g.wines_count, gt.name
    FROM most_used_grapes_per_country AS g
    JOIN grapes AS gt ON g.grape_id = gt.id
    ORDER BY g.grape_id, g.wines_count DESC
    LIMIT 5;
""")
top_5_grapes = cursor.fetchall()

# Write top 5 grapes to a text file
with open('top_5_grapes.txt', 'w') as f:
    f.write("Top 5 grapes and their corresponding names and taste:\n")
    for grape_id, wines_count, name in top_5_grapes:
        f.write(f"Grape ID: {grape_id}, Wine_count: {wines_count}, Grape Name: {name}\n")

# Country leaderboard based on average wine rating
cursor.execute("""
    SELECT c.name AS country_name, AVG(w.ratings_average) AS avg_rating
    FROM wines AS w
    JOIN regions AS r ON w.region_id = r.id
    JOIN countries AS c ON r.country_code = c.code
    GROUP BY c.name
    ORDER BY avg_rating DESC;
""")
country_ratings = cursor.fetchall()

# Write country leaderboard to a text file
with open('country_leaderboard.txt', 'w') as f:
    f.write("Country leaderboard based on average wine rating:\n")
    f.write("-------------------------------------------------\n")
    f.write("{:<30} {:<15}\n".format("Country", "Average Rating"))
    f.write("-------------------------------------------------\n")
    for country in country_ratings:
        f.write("{:<30} {:<15}\n".format(country[0], country[1]))

# Top 5 Cabernet Sauvignon recommendations for VIP client
cursor.execute("""
    SELECT v.name, v.ratings_average AS avg_rating, v.ratings_count AS rating_count, v.ratings_average * v.ratings_count AS rating_product, c.name AS country_name, r.name AS region_name, v.price_euros
    FROM vintages AS v
    JOIN wines AS w ON v.wine_id = w.id
    JOIN regions AS r ON w.region_id = r.id
    JOIN countries AS c ON r.country_code = c.code
    WHERE v.name LIKE '%Cabernet Sauvignon%'
    ORDER BY v.price_euros DESC
    LIMIT 5;
""")
top_cabernet_sauvignon = cursor.fetchall()

print("\nTop 5 Cabernet Sauvignon recommendations for VIP clients:")
for wine in top_cabernet_sauvignon:
    print(f"Wine: {wine[0]}, Country: {wine[4]}, Region: {wine[5]}, Average Rating: {wine[1]}, Rating Count: {wine[2]}, Rating Product: {wine[3]}, Price (Euros): {wine[6]}")

# Extract wine names and rating products
wine_names = [wine[0] for wine in top_cabernet_sauvignon]
rating_products = [wine[3] for wine in top_cabernet_sauvignon]

# Create custom colors
colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightsteelblue']

# Create bar chart
plt.figure(figsize=(10, len(top_cabernet_sauvignon) * 0.6))  # Adjust figure size based on the number of recommendations
bars = plt.barh(wine_names, rating_products, color=colors)

# Add text labels to the bars
for bar, rating, price in zip(bars, rating_products, [wine[6] for wine in top_cabernet_sauvignon]):
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"Rating Product: {rating}\nPrice (Euros): {price}", ha='left', va='center')

plt.xlabel('Rating Product')
plt.ylabel('Wine Name')
plt.title('Top 5 Cabernet Sauvignon Recommendations for VIP Clients')
plt.gca().invert_yaxis()  # Invert y-axis to display top-rated wines at the top

plt.tight_layout()  # Adjust layout to fit all text

# Save the plot as an image
plt.savefig('top_cabernet_sauvignon_plot.png')

# Show the plot
plt.show()