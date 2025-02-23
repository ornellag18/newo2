import re
from langchain.schema import HumanMessage

def serialize_memory(memory_messages):
    return [
        {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
        for msg in memory_messages
    ]

import re
import re

def text_to_html_list(text):
    # Detecta encabezados en negrita (Markdown)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Detecta texto en cursiva (Markdown)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Detecta palabras antes de ":" y las pone en negrita
    text = re.sub(r'(\b[\w\s]+\b):', r'<strong>\1:</strong>', text)
    
    # Detecta listas ordenadas
    ordered = re.findall(r'\d+\.\s[^\n]+', text)
    unordered = re.findall(r'-\s[^\n]+', text)
    
    # Construye listas HTML correctamente
    html_ordered = "<ol>" + "".join(f"<li>{item[3:].strip()}</li>" for item in ordered) + "</ol>" if ordered else ""
    html_unordered = "<ul>" + "".join(f"<li>{item[2:].strip()}</li>" for item in unordered) + "</ul>" if unordered else ""
    
    # Reemplaza la lista en el texto
    text = re.sub(r'\d+\.\s[^\n]+', '', text)
    text = re.sub(r'-\s[^\n]+', '', text)
    
    # Divide el texto en párrafos
    paragraphs = text.split('\n\n')
    html_paragraphs = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
    
    # Limpia los saltos de línea y espacios extras
    text = text.strip()
    
    # Combina todo en un solo HTML
    final_html = f"<div style='font-family: Arial, sans-serif; line-height: 1.6;'>{html_paragraphs}{html_ordered}{html_unordered}</div>"
    
    return final_html