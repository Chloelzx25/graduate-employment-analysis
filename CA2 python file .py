# import needed libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#import datasets
df1 = pd.read_csv(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\CA2 Datasets\(1) graduate employment survey modified.csv")
df2 = pd.read_csv(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\CA2 Datasets\(2) graduate employment survey modified .csv")
df3 = pd.read_csv(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\CA2 Datasets\EmployedResidentsAged15YearsOverbyGrossMonthlyIncomeFromEmploymentExcludingEmployerPlatformOperatorCPFContributionsHighestQualificationAttainedAndSex.csv")
df4 = pd.read_csv(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\CA2 Datasets\MedianGrossMonthlyIncomeFromEmploymentofFullTimeEmployedResidentsTotal.csv")
df5 = pd.read_csv(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\CA2 Datasets\EmploymentRateofResidentsAged25to64Total.csv")


#-------------------------------------------
#              DATA CLEANING
# ------------------------------------------
# merge df 1 and 2
keep_cols = ['employment_rate_overall', 'employment_rate_ft_perm','basic_monthly_mean', 'basic_monthly_median','gross_monthly_mean', 'gross_monthly_median', 'gross_mthly_25_percentile', 'gross_mthly_75_percentile', 'Key']
df2_clean = df2[keep_cols]

merged = pd.merge(df1, df2_clean, on='Key', how='inner')
merged = merged.drop(columns=['Key'])

numeric_cols = [ 'employment_rate_overall', 'employment_rate_ft_perm', 'basic_monthly_mean', 'basic_monthly_median', 'gross_monthly_mean', 'gross_monthly_median', 'gross_mthly_25_percentile', 'gross_mthly_75_percentile']
mask_bad_rows = pd.Series(False, index=merged.index)
for col in numeric_cols:
    mask_bad_rows |= (merged[col] == col)
merged = merged[~mask_bad_rows].copy()

for col in numeric_cols:
    merged[col] = merged[col].replace('na', np.nan)
    merged[col] = pd.to_numeric(merged[col], errors='coerce')

merged['year'] = pd.to_numeric(merged['year'], errors='coerce').astype('Int64')
merged = merged[(merged['year'] >= 2013) & (merged['year'] <= 2020)]

merged.to_csv('graduate_employment_survey_combined.csv', index=False)

#df3

salary_midpoints = {
    'Under $500': 250,
    '$500 to $999': 750,
    '$1,000 to $1,499': 1250,
    '$1,500 to $1,999': 1750,
    '$2,000 to $2,499': 2250,
    '$2,500 to $2,999': 2750,
    '$3,000 to $3,999': 3500,
    '$4,000 to $4,999': 4500,
    '$5,000 to $5,999': 5500,
    '$6,000 to $6,999': 6500,
    '$7,000 to $7,999': 7500,
    '$8,000 to $8,999': 8500,
    '$9,000 to $9,999': 9500,
    '$10,000 to $10,999': 10500,
    '$11,000 to $11,999': 11500,
    '$12,000 and over': 12500
}


#-------------------------------------------
#                 CHARTS
# ------------------------------------------

# pairplot
plt.figure()
merged['year_group'] = merged['year'].apply(lambda y: '2013-2016' if y <= 2016 else '2017-2020')
cols = ['employment_rate_overall', 'employment_rate_ft_perm', 'gross_monthly_median', 'basic_monthly_median']
g_pair = sns.pairplot(merged, vars=cols, diag_kind='kde', hue='year_group',plot_kws={'alpha': 0.5, 's': 20})
g_pair.fig.suptitle('Salary and Employment Rate Relationships', y=1.03)
g_pair.savefig(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\pairplot.png", dpi=300, bbox_inches="tight")

#linechart
plt.figure()
df_lineFiltered = df4[(df4['year'] >= 2013) & (df4['year'] <= 2020)]
plt.plot(df_lineFiltered['year'], df_lineFiltered['median_income_excl_emp_cpf'], marker='o', color='crimson')
plt.title("Median Income (Excl. Employer CPF), 2013-2020")
plt.xlabel("year")
plt.ylabel("median income")
plt.tight_layout()
plt.savefig(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\line_chart.png", dpi=300, bbox_inches="tight")

#bar chart
plt.figure()
df1_BarFiltered = df5[(df5['year'] >= 2013) & (df5['year'] <= 2020)]
plt.barh(df1_BarFiltered['year'], df1_BarFiltered['emp_rate'], color='crimson')
plt.title("Employment Rate, 2013-2020")
plt.xlabel("emp_rate")
plt.ylabel("year")
plt.tight_layout()
plt.savefig(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\bar_chart.png", dpi=300, bbox_inches="tight")

#kde chart
df3['degree_status'] = df3['highest_qualification'].apply(
    lambda x: 'Degree' if str(x).strip().lower() == 'degree' else 'Non-degree'
)
df3['employed'] = pd.to_numeric(df3['employed'], errors='coerce').fillna(0).astype(int)

kde_years = df3[df3['year'].isin([2013, 2020])].copy()
kde_years['income_midpoint'] = kde_years['gross_monthly_income_excl_emr_cpf'].map(salary_midpoints)
kde_years = kde_years.dropna(subset=['income_midpoint'])

kde_grouped = kde_years.groupby(
    ['year', 'degree_status', 'income_midpoint'], as_index=False
)['employed'].sum()

g_kde = sns.displot(
    data=kde_grouped,
    x='income_midpoint',
    weights='employed',
    hue='degree_status',
    col='year',
    kind='kde',
    fill=True,
    common_norm=False,
    clip=(0, 15000),
    alpha=0.4,
    height=5, aspect=1
)
g_kde.set_axis_labels('Gross Monthly Income (S$)', 'Density')
g_kde.set_titles('{col_name}')
g_kde.fig.suptitle('Income Distribution: Degree vs Non-Degree Holders, 2013 vs 2020', y=1.05)
g_kde.savefig(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\kde_chart.png", dpi=300, bbox_inches="tight")


# boxplot
box_df = df3[(df3["year"] >= 2013) & (df3["year"] <= 2020)].copy()
box_df = box_df[box_df["degree_status"].isin(["Degree", "Non-degree"])]

box_df["salary_midpoint"] = box_df["gross_monthly_income_excl_emr_cpf"].map(salary_midpoints)
box_df["employed"] = pd.to_numeric(box_df["employed"], errors="coerce").fillna(0).astype(int)

expanded = []
for _, row in box_df.iterrows():
    repeats = max(1, row["employed"] // 100)
    expanded.extend(
        [{"degree_status": row["degree_status"], "salary": row["salary_midpoint"]}] * repeats
    )
expanded_df = pd.DataFrame(expanded)

plt.figure(figsize=(8, 6))
sns.boxplot(
    data=expanded_df,
    x="degree_status",
    y="salary",
    hue="degree_status",
    palette="Set2",
    legend=False
)
plt.title("Estimated Salary Distribution\nDegree vs Non-degree (2013-2020)")
plt.xlabel("Education Level")
plt.ylabel("Estimated Monthly Salary (SGD)")
plt.tight_layout()
plt.savefig(r"C:\Users\chloe\OneDrive - Singapore Polytechnic\PDAS\CA2\boxplot.png", dpi=300, bbox_inches="tight")
