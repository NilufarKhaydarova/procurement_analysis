from process import df


df = df[['tovar', 'tovar_name']]

#value counts number should appear as column
df = df.value_counts(ascending=False)

print(df.head(5))

#excel
df.to_excel('tovar_sort_new.xlsx', index=False)