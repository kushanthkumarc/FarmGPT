import json
import re
import os

def clean_text(text):
    if not text: return ""
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove weird characters
    text = text.replace('\u00e2\u0080\u0093', '-').replace('\u00a0', ' ')
    text = text.replace('\u00e2\u0080\u0098', "'").replace('\u00e2\u0080\u0099', "'")
    text = text.replace('\u00e2\u0080\u00a0', ' ').replace('\u00c2', '')
    return text.strip()

def extract_pest_name(text):
    """
    Tries to find scientific names or specific pest names in the text.
    Scientific names are usually Two words starting with uppercase then lowercase.
    """
    # Look for common patterns like "Pest: Name" or scientific names
    match = re.search(r'([A-Z][a-z]+\s[a-z]+)', text)
    if match:
        return match.group(1)
    return "Unknown Pest"

def process_data():
    input_file = 'plant_data_columns.json'
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    cleaned_data = []
    
    for item in raw_data:
        common_name = item.get('Common_Name', '').strip()
        if common_name == "404 Not Found":
            continue
            
        sym = clean_text(item.get('Symptoms', 'N/A'))
        ident = clean_text(item.get('Identification', 'N/A'))
        etl = clean_text(item.get('ETL', 'N/A'))
        man = clean_text(item.get('Management_Methods', 'N/A'))
        
        # Check if we have actual data
        if sym == "N/A" and man == "N/A":
            continue
            
        # Try to recover a better name if it's generic
        sci_name = item.get('Scientific_Name', '').strip()
        display_name = common_name
        if display_name == "TNAU Agritech Portal" or not display_name:
            # Look in ETL or Symptoms for the name
            name_match = re.search(r'^([A-Z][A-Za-z\s]+),', etl)
            if name_match:
                display_name = name_match.group(1).strip()
            else:
                display_name = extract_pest_name(ident + " " + sym)

        # Merge fields for a comprehensive RAG doc
        full_content = f"Crop: {item.get('Crop')}\nPest/Issue: {display_name}\n"
        if sym != "N/A": full_content += f"Symptoms: {sym}\n"
        if ident != "N/A": full_content += f"Identification: {ident}\n"
        if etl != "N/A": full_content += f"Economic Threshold (ETL): {etl}\n"
        if man != "N/A": full_content += f"Management: {man}\n"

        structured_item = {
            "crop": item.get('Crop'),
            "pest_name": display_name,
            "content": full_content,
            "metadata": {
                "source": item.get('Source_URL'),
                "category": item.get('Crop')
            }
        }
        
        cleaned_data.append(structured_item)

    # Save structured JSON
    os.makedirs('data', exist_ok=True)
    output_json = 'data/rag_knowledge_base.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4)
        
    # Save a large text file for the simple ingest.py
    output_txt = 'data/rag_knowledge_base.txt'
    with open(output_txt, 'w', encoding='utf-8') as f:
        for entry in cleaned_data:
            f.write(entry['content'] + "\n" + "="*50 + "\n\n")

    print(f"Processed {len(raw_data)} items -> {len(cleaned_data)} valid RAG documents.")
    print(f"Output: {output_json} and {output_txt}")

if __name__ == '__main__':
    process_data()
