"""
BernardoBot 🤖 — Pregúntale a Bernardo (versión IA y con guasa)
Ejecutar:  streamlit run app.py
"""
import random
import streamlit as st

# ---------------------------------------------------------------- Config
st.set_page_config(page_title="BernardoBot", page_icon="🤖", layout="centered")

LINKEDIN = "https://www.linkedin.com/in/bernardo-meneses/"

SYSTEM_PROMPT = """Eres "BernardoBot", la versión IA (y bastante cachonda) de Bernardo Meneses,
ingeniero geotécnico/ambiental brasileño en Geosyntec Consultants Iberia (España).
Trabaja en seguridad de presas, cierre de balsas de relaves (tailings), minería,
proyectos en Galicia (San Ciprián) y Arabia Saudí. Le gustan Excel, JavaScript,
los modelos probabilísticos y los simuladores de Monte Carlo.

Responde SIEMPRE en español de España, con mucha guasa y cariño, a sus compañeros de trabajo.
Reglas de formato OBLIGATORIAS:
1. Empieza SIEMPRE con "¡Madre mía!" (puedes añadir algo detrás: "¡Madre mía, Paco!").
2. Después suelta un chiste o una pulla amistosa relacionada con la pregunta
   (si puedes, mete geotecnia, presas, relaves, factores de seguridad, Excel, el café de la oficina,
   los lunes, Galicia lloviendo, el calor de Arabia Saudí, algún "meu Deus" brasileño...).
3. Da una respuesta breve (2-5 frases). Si la pregunta es seria, contesta algo útil, pero con humor.
4. NO menciones los tokens: el sistema los añade al final automáticamente.
Nunca seas ofensivo ni cruel; es broma entre colegas. Nada de temas sensibles."""

# Respuestas de emergencia si no hay API key (modo "sin IA")
CHISTES_OFFLINE = [
    "¿Esa pregunta? Tiene un factor de seguridad de 0,3. Se me ha licuado el cerebro solo de leerla.",
    "Lo he metido en Excel, he hecho 10.000 simulaciones de Monte Carlo y en todas sale: 'pregúntale a otro'.",
    "Eso es como un talud sin drenaje: al principio parece buena idea y luego todo se desliza.",
    "Te respondo después del café. Del cuarto café, concretamente.",
    "En Galicia diríamos 'depende'. En Brasil, 'meu Deus'. Yo digo las dos cosas a la vez.",
    "Esa pregunta tiene más capas que un perfil geotécnico de San Ciprián.",
    "Lo consultaré con el piezómetro, que es el único que me entiende en esta oficina.",
    "Respuesta corta: sí. Respuesta larga: un informe de 84 páginas con 12 anexos. ¿Seguro que quieres la larga?",
    "Con esa pregunta has bajado el nivel freático de mi paciencia, pero aún aguanta.",
    "Hace más calor en esta pregunta que en una obra en Arabia Saudí en agosto.",
]


def coste_tokens_texto(n: int) -> str:
    frases = [
        f"🔥 Por cierto, acabas de quemar **{n} tokens** para preguntarme esto. El planeta te lo agradece.",
        f"🔥 Total: **{n} tokens** quemados. Eso ya es más que lo que gasta la impresora de la oficina.",
        f"🔥 Has fundido **{n} tokens** en esta pregunta. Se lo descuento de tu próximo café.",
        f"🔥 **{n} tokens** a la hoguera para esto. Madre mía, madre mía...",
        f"🔥 Contador de vergüenza: **{n} tokens** quemados. Lo pondré en el informe mensual.",
    ]
    return random.choice(frases)


def estimar_tokens(texto: str) -> int:
    # Aproximación: ~4 caracteres por token
    return max(1, len(texto) // 4)


def _secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def get_client():
    """IA open-source gratis vía Groq (https://console.groq.com/keys)."""
    key = _secret("GROQ_API_KEY")
    if not key:
        return None
    from groq import Groq
    return Groq(api_key=key)


def responder_ia(client, historial):
    model = _secret("MODEL", "openai/gpt-oss-120b")
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs += [{"role": m["role"], "content": m["content"]} for m in historial[-10:]]
    extra = {"reasoning_effort": "low"} if "gpt-oss" in model else {}
    resp = client.chat.completions.create(
        model=model, messages=msgs, max_tokens=1024, temperature=0.9, **extra
    )
    texto = resp.choices[0].message.content.strip()
    tokens = resp.usage.total_tokens
    return texto, tokens


def responder_offline(pregunta: str):
    texto = f"¡Madre mía! {random.choice(CHISTES_OFFLINE)}"
    # tokens "inventados" de forma dramática
    tokens = estimar_tokens(SYSTEM_PROMPT + pregunta + texto) + random.randint(50, 500)
    return texto, tokens


# ---------------------------------------------------------------- UI
st.title("🤖 BernardoBot")
st.caption(
    f"Pregúntale lo que quieras a [Bernardo]({LINKEDIN}) (versión IA). "
    "Responde con rigor geotécnico… más o menos."
)

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

client = get_client()

with st.sidebar:
    st.header("📊 Marcador de la vergüenza")
    st.metric("Tokens quemados en total", f"{st.session_state.total_tokens:,}".replace(",", "."))
    st.metric("Preguntas hechas", sum(1 for m in st.session_state.mensajes if m["role"] == "user"))
    if client is None:
        st.warning("Modo sin IA (no hay GROQ_API_KEY). Chistes de repuesto activados.")
    else:
        st.success(f"IA conectada 🧠 ({_secret('MODEL', 'openai/gpt-oss-120b')})")
    if st.button("🧹 Borrar conversación"):
        st.session_state.mensajes = []
        st.session_state.total_tokens = 0
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"], avatar="🧑‍💼" if m["role"] == "user" else "🤖"):
        st.markdown(m["display"])

pregunta = st.chat_input("Pregúntale algo a Bernardo…")
if pregunta:
    st.session_state.mensajes.append({"role": "user", "content": pregunta, "display": pregunta})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(pregunta)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Bernardo está calculando el factor de seguridad de tu pregunta…"):
            try:
                if client:
                    texto, tokens = responder_ia(client, st.session_state.mensajes)
                else:
                    texto, tokens = responder_offline(pregunta)
            except Exception as e:
                texto, tokens = responder_offline(pregunta)
                texto += f"\n\n_(La IA se ha ido a por café: {type(e).__name__})_"
        if not texto.lower().startswith("¡madre mía"):
            texto = "¡Madre mía! " + texto
        display = f"{texto}\n\n{coste_tokens_texto(tokens)}"
        st.markdown(display)

    st.session_state.total_tokens += tokens
    st.session_state.mensajes.append({"role": "assistant", "content": texto, "display": display})
    st.rerun()
