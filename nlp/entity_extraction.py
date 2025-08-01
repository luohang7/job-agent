# nlp/entity_extraction.py
import spacy
from config import SPACY_MODEL_NAME

try:
    print("正在加载SpaCy模型...")
    nlp = spacy.load(SPACY_MODEL_NAME)
    print("SpaCy模型加载成功。")
except OSError:
    print(f"错误: SpaCy模型 '{SPACY_MODEL_NAME}' 未找到。")
    print(f"请在终端运行: python -m spacy download {SPACY_MODEL_NAME}")
    nlp = None

def extract_skills_and_entities(text):
    if not nlp or not text or not isinstance(text, str):
        return {'skills': [], 'orgs': [], 'gpe': []}
    doc = nlp(text)
    known_skills = {"python", "java", "c++", "go", "javascript", "typescript", "react", "vue", "angular", "django", "flask", "spring boot", "tensorflow", "pytorch", "scikit-learn", "pandas", "mysql", "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp", "linux"}
    skills = []
    for token in doc:
        if token.text.lower() in known_skills: skills.append(token.text)
    for ent in doc.ents:
        if ent.text.lower() in known_skills: skills.append(ent.text)
    organizations = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    locations = [ent.text for ent in doc.ents if ent.label_ == 'GPE']
    return {'skills': list(set(skills)), 'orgs': list(set(organizations)), 'gpe': list(set(locations))}

def add_entities_to_dataframe(df):
    if df.empty or 'text_for_matching' not in df.columns: return df
    print("正在提取技能等实体信息...")
    entities = df['text_for_matching'].apply(extract_skills_and_entities)
    df['extracted_skills'] = [e['skills'] for e in entities]
    df['extracted_orgs'] = [e['orgs'] for e in entities]
    df['extracted_gpe'] = [e['gpe'] for e in entities]
    print("实体提取完成。")
    return df