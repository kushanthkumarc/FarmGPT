import pandas as pd
import json
import os

def merge_datasets():
    csv_path = 'rice_queries_enhanced.csv'
    json_path = 'data/rag_knowledge_base.json'
    output_path = 'data/final_unified_knowledge.json'
    
    merged_data = []

    # 1. Process the CSV (Conversational Queries)
    if os.path.exists(csv_path):
        print(f"Flattening CSV: {csv_path}...")
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            # Build a natural language "Scenario Paragraph"
            # This is key for RAG matching!
            content = f"""Farmer Scenario (Rice):
User Query: {row.get('Query', 'N/A')}
Crop Stage: {row.get('Stage', 'N/A')}
Diagnosis: {row.get('Possible Cause', 'N/A')}
Expert Solution: {row.get('Solution', 'N/A')}
Dosage Advice: {row.get('Dosage per Acre', 'N/A')}
Weather Dependency: {row.get('Weather Logic (Rain/No Rain)', 'N/A')}

[Regional Translations for NLP Matching]:
Kannada: {row.get('Query (Kannada)', 'N/A')} - {row.get('Solution (Kannada)', 'N/A')}
Hindi: {row.get('Query (Hindi)', 'N/A')} - {row.get('Solution (Hindi)', 'N/A')}
"""
            # Store in standard RAG schema
            merged_data.append({
                "source_type": "Conversational Mapping",
                "content": content,
                "metadata": {
                    "crop": "Rice",
                    "source": "Self-Curated Queries",
                    "type": "Scenario-Based"
                }
            })
    else:
        print(f"⚠️ CSV file {csv_path} fallback ignored.")

    # 2. Process the TNAU JSON (Technical Knowledge)
    if os.path.exists(json_path):
        print(f"Merging Technical JSON: {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            technical_data = json.load(f)
            # These are already in our RAG schema {content, metadata}
            for item in technical_data:
                item['source_type'] = "Technical Guide (TNAU)"
                merged_data.append(item)
    else:
        print(f"⚠️ JSON file {json_path} fallback ignored.")

    # 3. Save Final Unified Knowledge 
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4)

    print(f"\n✅ SUCCESS! Unified Knowledge Brain Created.")
    print(f"Total Combined RAG Documents: {len(merged_data)}")
    print(f"File Saved: {output_path}")

if __name__ == '__main__':
    merge_datasets()
