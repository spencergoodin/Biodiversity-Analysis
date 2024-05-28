# Import packages
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency

# Load data
observations_raw = pd.read_csv('observations.csv')
species_raw = pd.read_csv('species_info.csv')
observations = observations_raw.sort_values('observations').drop_duplicates(['scientific_name', 'park_name'])
species = species_raw.drop_duplicates(['scientific_name'])

data = pd.merge(observations, species, on='scientific_name')
data.fillna('No Intervention', inplace=True)

print(f'observations: {observations.shape}')
print(f'species: {species.shape}')

# Remember that each species will be listed four times in the 'plants' and 'animals' datasets, once for each park.
plants = data[(data.category == 'Vascular Plant') | (data.category == 'Nonvascular Plant')]
animals = data[(data.category != 'Vascular Plant') & (data.category != 'Nonvascular Plant')]

# Number of species in broad and narrow categorizations
print(f'Species of plants: {plants.scientific_name.nunique()}')
print(f'Species of animals: {animals.scientific_name.nunique()}')
print(species.category.groupby(species.category).count())

# Most common animal in each park
print(animals.sort_values(['observations'], ascending = False).groupby(['park_name']).head(1))

# Total number of animal sightings for each park
print(animals.groupby('park_name').sum('observations').sort_values(by='observations', ascending = False))

# Preparing bar chart for animal observations
plt.bar(animals.park_name.unique(), animals.observations.groupby(animals.park_name).sum().sort_values(ascending=False))
plt.ticklabel_format(useOffset=False,style = 'plain', axis='y')
plt.xticks(animals.park_name.unique(), ['Great Smoky Mountains\nNational Park', 'Bryce\nNational Park', 'Yosemite\nNational Park', 'Yellowstone\nNational Park'])
plt.xlabel('Location')
plt.ylabel('Total Animal Sightings')
plt.title('Number of Animal Sightings per Park')
plt.show(); plt.close()

# Table for conservation level by species category
category_threat = data[data['conservation_status'] != 'No Intervention'].groupby(['category', 'conservation_status']).scientific_name.nunique().unstack(level = 0)
# Reordering from default to order of urgency. This was very frustrating, if anyone reading this has a suggestion for how 
# the renaming proccess can be improved, please feel free to let me know.
category_threat.index = ([2,3,0,1])
category_threat.sort_index(inplace=True)
category_threat.index = (['Species of Concern','Threatened','Endangered','In Recovery'])
# Plotting conservation level by species
category_threat.plot(kind = 'bar', stacked = True, title = 'Species Count by Conservation Status', xlabel = 'Conservation Status', ylabel = 'Number of Species')
plt.xticks(rotation=0)
category_threat.fillna(0, inplace=True)
print(category_threat)
plt.show(); plt.close()

# Table for percentage of species threatened per category
threat_percentages = data.groupby('category').nunique()
threat_percentages['species'] = data.groupby('category').scientific_name.nunique()
threat_percentages['threatened'] = data[data['conservation_status'] != 'No Intervention'].groupby('category').scientific_name.nunique()
threat_percentages['percentage'] = (data[data['conservation_status'] != 'No Intervention'].groupby('category').scientific_name.nunique()) / (data.groupby('category').scientific_name.nunique())
threat_percentages = threat_percentages[['species','threatened','percentage']]
print(threat_percentages)

# Adding column for proportion of conservation effort to total conservation efforts for each category
threat_percentages['proportion'] = (threat_percentages.threatened)/(threat_percentages.threatened.sum())
threat_percentages.sort_values('proportion', ascending = False, inplace = True)
# Plotting proportions by category
category_labels = threat_percentages.index.tolist()
for x in range(len(category_labels)):
    category_labels[x] = category_labels[x].replace(' Plant', '\nPlant')

threat_percentages.plot(kind = 'bar', y='proportion', legend = None, title = 'Proportion of Conservation Efforts by Wildlife Category', xlabel = 'Category', ylabel = 'Proportion')
plt.xticks(range(len(threat_percentages.index)), category_labels, rotation=20)
print(threat_percentages.proportion)
plt.show(); plt.close()

# Preparing crosstab for plant/animal conservation comparison
ancount =  animals.groupby('category').scientific_name.nunique().sum()
anthreat = animals[animals['conservation_status'] != 'No Intervention'].groupby('category').scientific_name.nunique().sum()
plcount = plants.groupby('category').scientific_name.nunique().sum()
plthreat = plants[plants['conservation_status'] != 'No Intervention'].groupby('category').scientific_name.nunique().sum()

# Ratio information
print(anthreat/plthreat) # Threatened animals:threatened plants
print(anthreat/ancount) # % animals needing conservation
print(plthreat/plcount) # % plants needing conservation

# Chi**2 Test
threat_ratios = np.array([[anthreat, plthreat],[ancount, plcount]])
result = chi2_contingency(threat_ratios)
print(f'Chi Squared Statistic (correlation): {result.statistic}\nP-value (significance): {result.pvalue}')