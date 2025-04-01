
import pandas as pd
import numpy as np


#merges all professor related csvs, taking care of duplicates.


#combines the fields together, prioritizing the non-null/longer one

def merge_columns(merged_df):
    aliases={}
    combine_first_arr=['instructor', 'title']
    for col_name in combine_first_arr:
        if col_name + "_new" in merged_df.columns:
            merged_df[col_name] = np.where(
                merged_df[col_name + "_new"].notna() & merged_df[col_name].notna(),  # If both are not null
                np.where(merged_df[col_name].str.len() >= merged_df[col_name + "_new"].str.len(),  
                        merged_df[col_name],  # Pick column with longer value
                        merged_df[col_name + "_new"]), 
                merged_df[col_name].combine_first(merged_df[col_name + "_new"])  # Otherwise, use the non-null value
            )
    # Add to aliases with new_name as key and old_name as value
    if "instructor_new" in merged_df.columns:
        for index, row in merged_df.iterrows():
            if pd.notna(row['instructor']) and pd.notna(row['instructor_new']):
                aliases[row['instructor_new']] = row['instructor']
    for col_name in combine_first_arr:
        if (col_name + "_new") in merged_df.columns:
            merged_df = merged_df.drop(columns=[col_name + "_new"])
    print(len(aliases))
    return merged_df, aliases
 
def is_subset(name1, name2):
    words1, words2 = set(name1.split()), set(name2.split())  
    return words1 < words2 

 
 # merge rows where first letter of the first name and the last name are the same.
# also keep track of the names that were replaced
def merge_rows(merged_df):
    aliases={}
    # a bunch of temp fields used for sorting priority.
    
    merged_df['first_letter'] = merged_df['instructor'].str.split().str[0].str.replace('.', '').str[0]  # First letter of first name
    merged_df['last_name'] = merged_df['instructor'].str.split().str[-1]  # Last name (last word in name)
    merged_df['has_email'] = merged_df['email'].notna().astype(int) 
    merged_df['name_length'] = merged_df['instructor'].str.len()  
    merged_df['has_ampersand'] = merged_df['instructor'].str.contains('and|&', case=False, na=False)
    merged_df = merged_df.sort_values(
        # we sort by  the df using hte below fields
        by=['last_name', 'first_letter', 'has_ampersand', 'has_email', 'name_length'],
        ascending=[True, True, True, False, False]
        )

    merged_df = merged_df.drop(columns=['has_email', 'name_length', 'has_ampersand'])
    
    for _, row in merged_df.iterrows():
        key = (row['last_name'], row['first_letter']) 
        # If this key already exists, it means a longer/better version was kept earlier
        if key in aliases:
            aliases[row['instructor']] = aliases[key] 
        else :
            
            aliases[key] = row['instructor']  
    
    
    
    for _, group in merged_df.groupby('last_name'): 
        true_name=""
        to_remove = []
        for i, (idx1, row) in enumerate(group.iterrows()):
            
            if i == 0:
                true_name = row['instructor']
            
            elif is_subset(row['instructor'], true_name):
                to_remove.append(idx1) 
                
        merged_df = merged_df.drop(to_remove)
    merged_df=merged_df.drop_duplicates(subset=['last_name', 'first_letter'], keep='first')
    merged_df = merged_df.drop(columns=['first_letter', 'last_name'])
    # Remove the tuple helper keys from alias
    aliases = {k: v for k, v in aliases.items() if isinstance(k, str) and k!=v}    
    print(len(aliases))
    return merged_df, aliases

aliases={}

df1 = pd.read_csv('history_classes/data/instructor_emails.csv') # emails scraped from syllabus 
df2 = pd.read_csv('history_classes/data/personal_page.csv') # emails from faculty page
df3 = pd.read_csv('history_classes/data/prof_info.csv') # professor+title from course website. Not used for stats courses, because we don't have course info online for them.

df1['instructor'] = df1['instructor'].str.replace('.', '').str.replace("\xa0", " ")
df2['instructor'] = df2['instructor'].str.replace('.', '').str.replace("\xa0", " ")
df3['instructor'] = df3['instructor'].str.replace('.', '').str.replace("\xa0", " ")
merged_df = df1.merge(df2, on='email', how='outer', suffixes=('', '_new'))

merged_df,aliases1=merge_columns(merged_df)



merged_df=merged_df.merge(df3[['instructor', 'title']], on='instructor', how='outer', suffixes=('', '_new'))

# multiple alias dictionaries due to issues with the dict being overwritten.
merged_df, aliases2=merge_columns(merged_df)
merged_df,aliases3 = merge_rows(merged_df)


merged_df.to_csv('history_classes/merged/instructor_info.csv', index=False)

# update office hour instructor names using aliases
df4 = pd.read_csv('history_classes/merged/office_hours.csv') # emails from faculty page
df4['instructor'] = df4['instructor'].replace(aliases1).replace(aliases2).replace(aliases3)
df4.to_csv('history_classes/merged/office_hours.csv', index=False)
