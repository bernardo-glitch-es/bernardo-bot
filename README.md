# 🤖 BernardoBot

Chat de broma para los compañeros: pregúntale lo que quieras a Bernardo (versión IA).
Cada respuesta empieza con **"¡Madre mía!"**, suelta un chiste y te dice cuántos tokens has quemado.

IA: modelo open-weight **gpt-oss-120b** servido gratis por [Groq](https://console.groq.com)
(Groq retiró los modelos Llama en agosto de 2026). Cambia el modelo con `MODEL` en los secrets.
Sin clave funciona igual con chistes de repuesto.

## Ejecutar en local
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # y pega tu GROQ_API_KEY
streamlit run app.py
```

## Streamlit Community Cloud
Despliega `app.py` y añade en *Settings → Secrets*:
```toml
GROQ_API_KEY = "gsk_..."
```
