# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt    
import seaborn as sns

# Raw imported data
data_raw = pd.read_csv("sheet.csv",sep =';')

# Remove nan empty rows
df = data_raw[data_raw['Persona'].notna()]

# Manually fix persona naming mismatch
df = df.replace('Product Designer ', 'Product Designer')
df = df.replace(['DSLT','UX Architect ','Overall', 'SAP Consulting'],'Consulting/Partner')
df = df.replace('Developer', 'Product Developer')
df = df.replace('End-user', 'Product Manager')
df = df.replace('Fixing UX consequences and not root causes', 'Fixing UX consequences and not root causes')
df = df.replace('Bad design practices ', 'Bad design practices')

# Get unique Personas
personas_count = []
personas = df['Persona'].value_counts().reset_index().rename(columns={"index": "Persona", 0: "count"})['Persona']
uniqppl = df['Feedback provided by'].value_counts().reset_index().rename(columns={"index": "name", 0: "count"})
unique_ps_for_all = df['Title'].value_counts().reset_index().rename(columns={"index": "Title", 0: "count"})

# Read unique problem statements (titles) for each Persona
all_problem_statements = pd.DataFrame()
problem_statements = pd.DataFrame()
for p in personas:
  #print('Processing data for ',p,'...')
  # Cout most occuring problem statements
  curr_df = df.loc[df['Persona'] == p]
  counts = curr_df['Title'].value_counts().reset_index().rename(columns={"index": "Title", 0: "count"})
  # Add persona to the statements
  counts = counts.assign(Persona = p)
  all_problem_statements = all_problem_statements._append(counts)
  # Select only first 6 most occuring
  counts = counts.head(6)
    
  # Get Rank values for the selected problem statements and compute mean rank
  df1 = curr_df[['Title', 'Rank']]  
  df1 = df1.loc[df1['Title'].isin(counts['Title'])]
  # Replace empty Rank rows with nan to compute mean
  df1 = df1.replace(r'^\s*$', np.nan, regex=True)
  df1['Rank'] = pd.to_numeric(df1['Rank'])
  df2 = df1.groupby(['Title']).mean().reset_index().rename(columns={"index": "Title", 0: "Rank"})
  a =df1.groupby(['Title']).std().reset_index().rename(columns={"index": "Title", "Rank": "STD"})
  df2['STD'] = a['STD']
  rnk = pd.DataFrame()
  
  # Plot
  boxplot = sns.boxplot(data=df1, x="Rank", y="Title",width=.5,showmeans=True, meanprops={"color": "r", "linewidth": 2},boxprops={"facecolor": ('#C7E4FB')})
  title_boxplot = p
  plt.rcParams['font.family'] = 'serif'  
  plt.title( 'Rank Score Distribution for ' + title_boxplot )
  plt.suptitle('') # that's what you're after
  plt.ylabel('Unique problem statement')
  plt.rcParams['figure.dpi'] = 300
  plt.show()


  # Sort calculated mean Rank values according to problem statement occurance (this should be a function :))))
  for r in counts['Title']:
      rnk = rnk._append(df2.loc[df2['Title']== r])
  rnk = rnk.reset_index()
  # add mean Rank to problem statements
  counts = counts.assign(Rank = rnk['Rank'])
  counts = counts.assign(STD = rnk['STD'])
  problem_statements = problem_statements._append(counts)
  # Count no of participants
  personas_count.append(len(curr_df['Feedback provided by'].unique()))

# Filtering data for "Product Designer" persona
pd_data = df[df['Persona'] == 'Product Designer']
# Sorting by mean rank for better visualization
pd_data_sorted = pd_data.sort_values('Rank', ascending=True)

# Count no. of participants, unique problem statements and no. of answers (table 3 overleaf)
overwiew_table = pd.DataFrame()
overwiew_table['Role'] = df['Persona'].value_counts().reset_index().rename(columns={"index": "Persona", 0: "count"})['Persona']
overwiew_table['Number of Participants'] = personas_count
overwiew_table['Unique Problem Statements'] = all_problem_statements['Persona'].value_counts().reset_index().rename(columns={"index": "Persona", 0: "count"})['count']

all_counts = all_problem_statements.groupby('Persona',sort=False)['count'].sum().reset_index().rename(columns={"index": "Role", 0: "count"})
rr = pd.DataFrame()
for e in overwiew_table['Role']:
    rr = rr._append(all_counts.loc[all_counts['Persona']== e])
rr = rr.reset_index()
overwiew_table['Total answers']  =  rr['count']
overwiew_table.loc['Total']= overwiew_table.sum()

srt_problem_statements = problem_statements.sort_values(by=['Rank'], ascending=True)
srt_problem_statements = srt_problem_statements.rename(columns={'Rank': 'Mean Rank'})

# export to csv
problem_statements.to_csv('out.csv', index=False)
df1.to_csv('df1.csv', index=False)
srt_problem_statements.to_csv('srt_problem_statements.csv', index=False)