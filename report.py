import sqlite3
import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

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

# Extract wine names and rating products for plotting
wine_names = [wine[0] for wine in top_10_wines]
rating_products = [wine[3] for wine in top_10_wines]

# Define custom colors for the bars
colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightsteelblue', 
          'lightpink', 'lightseagreen', 'lightgray', 'lightblue', 'lightyellow']

# Create bar chart for top 10 wines to increase sales
plt.figure(figsize=(12, 8))  # Adjust figure size for better readability or fit to the page
bars = plt.barh(wine_names, rating_products, color=colors)

# Add rating product values as text on the bars
for bar, rating in zip(bars, rating_products):
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, str(rating), ha='left', va='center')

plt.xlabel('Rating Product')
plt.ylabel('Wine Name')
plt.title('Top 10 Wines to Increase Sales for Wiwino')
plt.gca().invert_yaxis()  # Invert y-axis to display top-rated wines at the top
plt.tight_layout()  # Adjust layout to fit all text within the plot

# Save the plot as an image buffer
plot_image_buffer = io.BytesIO()
plt.savefig(plot_image_buffer, format='png')
plot_image_buffer.seek(0)

# Convert plot image buffer to reportlab Image object and resize it
plot_image = Image(plot_image_buffer, width=letter[1]*0.9, height=letter[0]*0.7)

# Close the plot to release memory
plt.close()

# Generate the PDF report
doc = SimpleDocTemplate("vivino_report.pdf", pagesize=landscape(letter))  # Change to landscape orientation
styles = getSampleStyleSheet()
style_heading = styles['Heading1']
style_body = styles['BodyText']

# Add title to the report
doc_title = Paragraph("Vivino Report", style_heading)
doc_content = [doc_title, Spacer(1, 12)]

# Add the plot to the report
doc_content.append(plot_image)
doc_content.append(Spacer(1, 12))

# Add top 10 wines text content
top_10_wines_text = "Top 10 wines to increase sales for Wiwino:\n"
for wine in top_10_wines:
    top_10_wines_text += f"Wine: {wine[0]},  Average Rating: {wine[1]}, Rating Count: {wine[2]}, Rating Product: {wine[3]}\n"
top_10_wines_paragraph = Paragraph(top_10_wines_text, style_body)
doc_content.append(top_10_wines_paragraph)
doc_content.append(Spacer(1, 12))

# Add other text files to the report
text_files = ['priority_countries.txt', 'top_3_wines.txt', 'winery_names.txt', 
              'taste_related_wines.txt', 'taste_related_keywords.txt', 
              'wine_group_names.txt', 'top_5_grapes.txt', 'country_leaderboard.txt', 
              'top_cabernet_sauvignon.txt']
for file in text_files:
    with open(file, 'r') as f:
        file_content = f.read()
        file_paragraph = Paragraph(file_content, style_body)
        doc_content.append(file_paragraph)
        doc_content.append(Spacer(1, 12))

# Build the PDF report
doc.build(doc_content)
