import pandas as pd

# Read both CSVs
df1 = pd.read_csv("cleaned_classes(in).csv")
df2 = pd.read_csv("pdf_syllabi_info.csv")

# Rename the 'Instructor' column to 'instructor' to match the column name in df1
df2 = df2.rename(columns={"Instructor": "instructor"})

# Merge df2 into df1 on SEC_NAME and SEC_TERM (left join)
merged = df1.merge(df2[["SEC_NAME", "SEC_TERM", "instructor"]],
                   on=["SEC_NAME", "SEC_TERM"],
                   how="left",
                   suffixes=("", "_from_df2"))

# If instructor is missing in df1 but present in df2, fill it in
merged["instructor"] = merged["instructor"].combine_first(merged["instructor_from_df2"])

# Drop helper column
merged = merged.drop(columns=["instructor_from_df2"])

# Save final result
merged.to_csv("cleaned_classes.csv", index=False)
