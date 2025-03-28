# -*- coding: utf-8 -*-
"""Geo_Analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_N140z5WZ59bGDM1KTPNTXAGP2w7PSPD

Instructions:
1. Insert your CSV file path or use Colab's file uploader. Dataset example [here](/content/geoexperiment_dataset.csv).
2. The notebook runs t-tests comparing Cities.
3. The result of the t-test shows an insight for each city.
3. ROAS is calculated and visualized for decision-making.
4. Easily switch datasets by re-uploading and rerunning the cells.

This section of the code sets up the environment for data analysis by importing necessary libraries.
"""

# Geo Experiment Analysis Notebook

# ✅ Import Libraries
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
!pip install morethemes
import morethemes as mt
mt.set_theme("minimal")

"""This section of the code is specifically designed for use within Google Colab, an online environment for running Python code. It allows the user to easily upload a CSV file and load it into a pandas DataFrame for analysis."""

# ✅ Colab File Uploader
from google.colab import files
uploaded = files.upload()
df = pd.read_csv(next(iter(uploaded)))

"""This step is done to avoid division by zero errors when calculating metrics like Return on Ad Spend (ROAS), which involves dividing response or revenue by cost. It ensures that only cities with non-zero advertising costs are included in the analysis."""

# ✅ Data Cleaning
df['response'] = df['response'].str.replace(',', '').astype(float)
df = df[df['cost'] != 0]  # Exclude cities where cost is 0

"""This part of the code is designed to calculate and display summary statistics for each city in your dataset. It essentially groups the data by city and then computes various metrics for each group."""

# ✅ Data Summary
city_summary = df.groupby('city').agg(
    total_cost=('cost', 'sum'),
    total_response=('response', 'sum'),
    avg_cost=('cost', 'mean'),
    avg_response=('response', 'mean'),
    count=('response', 'count')
).reset_index()

print("\nCity Summary:")
print(city_summary)

"""This code visualizes the relationship between advertising cost and response for different cities using scatter plots and trend lines. It also calculates and displays the R-squared value to assess the strength of the relationship in each city. This helps in understanding how advertising spending affects response across different geographical locations."""

mt.set_theme("minimal")

# Ensure 'date' is in datetime format
df['date'] = pd.to_datetime(df['date'])

# Set up FacetGrid for multiple cities
g = sns.FacetGrid(df, col="city", col_wrap=3, height=4, sharex=True, sharey=True)

# Function to add scatter, trend line & R²
def plot_regression(data, **kwargs):
    ax = plt.gca()

    # Scatterplot
    sns.scatterplot(data=data, x="cost", y="response", ax=ax, color="blue", alpha=0.5, label="Data Points")

    # Linear regression
    if len(data) > 1:
        X = data["cost"].values.reshape(-1, 1)
        y = data["response"].values
        model = LinearRegression().fit(X, y)
        y_pred = model.predict(X)

        # Plot regression line
        sns.lineplot(x=data["cost"], y=y_pred, ax=ax, color="red", label="Trend Line")

        # Compute & display R²
        r2 = r2_score(y, y_pred)
        ax.text(0.05, 0.95, f"R² = {r2:.2f}", transform=ax.transAxes, fontsize=10, verticalalignment='top')

    # Add legend
    ax.legend()

# Apply function to each subplot
g.map_dataframe(plot_regression)

# Improve layout
g.set_titles(col_template="{col_name}")  # Show city names
g.set_axis_labels("Cost", "Response")
g.fig.suptitle("Cost vs Response Relationship by City", fontsize=16)

plt.tight_layout()
plt.show()

"""In simpler terms, this code analyzes how changes in advertising spending (cost) affect the response in each city. It helps determine if the relationship is statistically significant and how well the model fits the data. The results are then organized and displayed for easy interpretation."""

# Group data by city and run a regression (response ~ cost) for each city
results = {}
for city, city_data in df.groupby("city"):
    X = city_data["cost"]
    y = city_data["response"]

    # Add a constant term for the intercept in regression
    X = sm.add_constant(X)

    # Fit the linear regression model
    model = sm.OLS(y, X).fit()

    # Store the results (p-value and R-squared)
    results[city] = {
        "p_value": model.pvalues["cost"],
        "r_squared": model.rsquared
    }

# Convert results to a DataFrame for better visualization
results_df = pd.DataFrame.from_dict(results, orient="index").reset_index()
results_df.columns = ["city", "p_value", "r_squared"]
results_df.sort_values(by="p_value", inplace=True)  # Sort by significance

# Display the top 10 results
print(results_df.head(10))

"""**How the Interpretation Works:**

**p_value < 0.05**: This indicates that the relationship between ad spend (cost) and response is statistically significant. In simpler terms, it's unlikely that the observed relationship is due to random chance.

r**_squared >= 0.5**: This suggests a moderate to strong relationship between ad spend and response. A higher r_squared means the model explains a larger proportion of the variance in the response variable.

**Interpretations:**

**Significant and strong:** If both conditions (low p_value and high r_squared) are true, it means ad spend has a clear and positive impact on response in that city.

**Significant but weak:** If the p_value is low but r_squared is below 0.5, it indicates a statistically significant relationship, but ad spend might not be the primary driver of response. Other factors might be influencing the results.

**Not significant:** If the p_value is above 0.05, it suggests that ad spend does not have a statistically significant impact on response in that city.
By adding this interpretation column, the results become more informative and actionable. You can now easily identify cities where ad spend is most effective and make data-driven decisions for your campaigns.
"""

# Add interpretation based on p-value and r-squared
results_df['interpretation'] = ''  # Add a new column for interpretation
for index, row in results_df.iterrows():
    p_value = row['p_value']
    r_squared = row['r_squared']
    city = row['city']

    if p_value < 0.05:  # Check for statistical significance
        if r_squared >= 0.5:  # Check for moderate to strong relationship
            interpretation = f"In {city}, ad spend has a statistically significant and strong positive impact on response (p={p_value:.3f}, R²={r_squared:.3f})."
        else:
            interpretation = f"In {city}, ad spend has a statistically significant but weak impact on response (p={p_value:.3f}, R²={r_squared:.3f}). Consider other factors."
    else:
        interpretation = f"In {city}, ad spend does not have a statistically significant impact on response (p={p_value:.3f}, R²={r_squared:.3f})."

    results_df.loc[index, 'interpretation'] = interpretation  # Update the DataFrame

# Display the results with interpretation
for _, row in results_df.iterrows():
    print(row['interpretation'])

# Assuming 'results_df' is your DataFrame with city, p_value, and r_squared
mt.set_theme("minimal")
# --- Visualization for p-value ---
plt.figure(figsize=(10, 6))
sns.stripplot(data=results_df, x='city', y='p_value', hue='city', palette='viridis',
              jitter=True, dodge=True, legend=False)  # Assign x to hue and set legend=False
plt.title('P-value by City')
plt.xlabel('City')
plt.ylabel('P-value')
plt.xticks(rotation=45, ha='right')
plt.axhline(y=0.05, linestyle='--', color='red', label='Significance Threshold (p=0.05)')
plt.legend()
plt.tight_layout()
plt.show()

# --- Visualization for r-squared ---
plt.figure(figsize=(10, 6))
sns.stripplot(data=results_df, x='city', y='r_squared', hue='city', palette='magma',
              jitter=True, dodge=True, legend=False)  # Assign x to hue and set legend=False
plt.title('R-squared by City')
plt.xlabel('City')
plt.ylabel('R-squared')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

"""This section takes the results of the t-tests that were calculated earlier and organizes them into a neat table (DataFrame) and then prints that table to the console for you to see. This makes it much easier to interpret the results compared to having them in a less organized format."""

# ✅ ROAS Calculation
city_summary['ROAS'] = city_summary['total_response'] / city_summary['total_cost']

print("\nROAS by City:")
print(city_summary[['city', 'ROAS']])

# ✅ Visualization
# Set the style to "whitegrid" for a clean background
mt.set_theme("minimal")

# Create a figure with transparent background
plt.figure(figsize=(12, 7), dpi=80)

# Create the barplot with 'viridis' color palette
ax = sns.barplot(data=city_summary, x='city', y='ROAS', palette='viridis')

# Add title and labels with more styling for better presentation
plt.title('ROAS by City', fontsize=16, weight='bold')
plt.xlabel('City', fontsize=12)
plt.ylabel('ROAS', fontsize=12)

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Add data labels above each bar for clarity
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}',
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                fontsize=12, color='black',
                xytext=(0, 5), textcoords='offset points')

# Set the background of the figure and axes to transparent
plt.gcf().patch.set_alpha(0.0)
ax.set_facecolor('none')

# Show the plot
plt.show()