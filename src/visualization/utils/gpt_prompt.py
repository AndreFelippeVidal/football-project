import openai

def generate_gpt_prompt(df_results, table_name):
    prompt = f"""
    The following results from the data validation were found for the table {table_name}

    {df_results.to_string(index=False)}

    For each column:
    - Explain the null values impact.
    - Suggest corrective actions.
    - Create a tabular report with the following fields: Column Name, % of Nulls, Impact and Recommended Actions. 
      For this report, under Column name column you must aggregate the rows with the same values for null, impact and actions in the same row.
    - Add a final column in the report with emojis, following below rules:
      - If the nulls percentage is bewteen 1% and 10%, add a ⚠️ (warning emoji)
      - If the nulls percetahe is greater than 10%, add a ❌ (red X emoji).    
    Note: The last column is the only one that should have emojis and its name should be status.

    Be concise, only apply more context if requested.
    Always start your answer with the tabular report, and apply any other thing after.
    """
    return prompt

def get_gpt_report(message):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a specialist in data quality."},
            {"role": "user", "content": message},
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content