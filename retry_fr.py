import json
import os
import time
from deep_translator import GoogleTranslator

langs = {
    'hi': 'hindi',
    'mr': 'marathi',
    'kn': 'kannada',
    'ml': 'malayalam',
    'te': 'telugu',
    'ta': 'tamil',
    'es': 'spanish',
    'fr': 'french'
}

with open('Frontend/locales/en/translation.json', 'r', encoding='utf-8') as f:
    en_data = json.load(f)

def translate_dict(d, target_lang):
    print(f"Translating {len(d)} keys to {target_lang}...")
    translator = GoogleTranslator(source='en', target=target_lang)
    translated_d = {}
    for k, v in d.items():
        retry_count = 0
        while retry_count < 3:
            try:
                translated_d[k] = translator.translate(v)
                break
            except Exception as e:
                print(f"Error for {k}. Retrying...")
                retry_count += 1
                time.sleep(2)
        if retry_count == 3:
            # simple manual fallback for emojis or failed
            translated_d[k] = v
    return translated_d

for lang_code, lang_name in langs.items():
    os.makedirs(f'Frontend/locales/{lang_code}', exist_ok=True)
    out_path = f'Frontend/locales/{lang_code}/translation.json'
    
    lang_data = {}
    if os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
    
    keys_to_translate = {k: v for k, v in en_data.items() if k not in lang_data}
    
    if keys_to_translate:
        new_translations = translate_dict(keys_to_translate, lang_code)
        lang_data.update(new_translations)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, ensure_ascii=False, indent=2)
        print(f"Updated {lang_code}.")
    else:
        print(f"Skipping {lang_code}, all keys translated.")

print("Done translating French frontend.")
