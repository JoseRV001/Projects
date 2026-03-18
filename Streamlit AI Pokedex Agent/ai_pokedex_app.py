import streamlit as st
from pokedex_agent import chat_with_claude,chat_with_openai

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PokéDex AI",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling the main UI of the App, including background, fonts, and message bubbles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    .stApp { background-color: #1a1a2e; }
    h1 { font-family: 'Press Start 2P', monospace; font-size: 18px !important; color: #ffcb05 !important; text-shadow: 2px 2px 0px #3d7dca; }
    .user-msg {
        background: linear-gradient(135deg, #16213e, #0f3460);
        border-left: 4px solid #3d7dca;
        padding: 12px 16px; border-radius: 8px; margin: 8px 0;
        color: #e0eaff; font-size: 14px;
    }
    .assistant-msg {
        background: linear-gradient(135deg, #1a2a1a, #0f2d0f);
        border-left: 4px solid #ffcb05;
        padding: 12px 16px; border-radius: 8px; margin: 8px 0;
        color: #fffde0; font-size: 14px;
    }
    .poke-name {
        font-family: 'Press Start 2P', monospace;
        font-size: 14px; color: #ffcb05; text-transform: uppercase; margin: 8px 0;
    }
    .poke-type {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-size: 11px; font-weight: bold; color: white;
        margin: 2px; text-transform: uppercase;
    }
    .tool-badge {
        display: inline-block; background: #0f3460; color: #3d7dca;
        font-size: 11px; padding: 2px 8px; border-radius: 12px; margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)
#Colors used to repsent the different Pokeon Types
TYPE_COLORS = {
    "normal": "#A8A878", "fire": "#F08030", "water": "#6890F0", "electric": "#F8D030",
    "grass": "#78C850", "ice": "#98D8D8", "fighting": "#C03028", "poison": "#A040A0",
    "ground": "#E0C068", "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820",
    "rock": "#B8A038", "ghost": "#705898", "dragon": "#7038F8", "dark": "#705848",
    "steel": "#B8B8D0", "fairy": "#EE99AC",
}

#AI Agent Model options for OpenAI & Anthropic
ANTHROPIC_MODELS = ["claude-opus-4-5", "claude-sonnet-4-5"]
OPENAI_MODELS    = ["gpt-4o", "gpt-4o-mini"]

# Session State
#default values for session state variables that appear on streamlit app before user interference
for key, default in {
    "messages": [],
    "provider": "Anthropic",
    "anthropic_key": "",
    "openai_key": "",
    "model": ANTHROPIC_MODELS[0],
    "temperature": 0.5,
    "max_tokens": 1024,
    "last_pokemon": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

#Sidebar config
with st.sidebar:
    st.markdown("⚙️ Settings")
    st.subheader("🤖 AI Agent Provider")
    provider = st.radio("Provider", ["Anthropic", "ChatGPT"], horizontal=True,
                        index=0 if st.session_state.provider == "Anthropic" else 1)

    # Reset model when provider changes
    if provider != st.session_state.provider:
        st.session_state.provider = provider
        st.session_state.model = ANTHROPIC_MODELS[0] if provider == "Anthropic" else OPENAI_MODELS[0]
        st.session_state.messages = []
        st.session_state.last_pokemon = None

    st.divider()

    # API key input — shown for whichever provider is active
    if st.session_state.provider == "Anthropic":
        st.subheader("🔑 Anthropic API Key")
        key_input = st.text_input("API Key", type="password",
                                   value=st.session_state.anthropic_key, placeholder="sk-ant-...")
        if key_input:
            st.session_state.anthropic_key = key_input
    else:
        st.subheader("🔑 OpenAI API Key")
        key_input = st.text_input("API Key", type="password",
                                   value=st.session_state.openai_key, placeholder="sk-...")
        if key_input:
            st.session_state.openai_key = key_input

    st.divider()
    st.subheader("🧠 Model")
    model_options = ANTHROPIC_MODELS if st.session_state.provider == "Anthropic" else OPENAI_MODELS
    # Keep current model selected if still valid, else reset to first option
    current_model = st.session_state.model if st.session_state.model in model_options else model_options[0]
    st.session_state.model = st.selectbox("Model", model_options,
                                           index=model_options.index(current_model))
    
    st.divider()
    st.subheader("🎛️ Generation Parameters")
    st.session_state.temperature = st.slider("Temperature 🌡", 0.0, 1.0, st.session_state.temperature, 0.05)
    st.session_state.max_tokens = st.slider("Max Tokens 🪙", 256, 2048, st.session_state.max_tokens, 64)

    st.divider()
    st.subheader("🔎Example Clues")
    st.markdown("""
Try describing a Pokémon like:
- *"Tiny yellow mouse, red cheeks, lightning bolt tail"*
- *"Fire/flying bird with long tail feathers"*
- *"Ghost type, hides in shadows, loves to lick people"*
- *"Sleeps 18 hours a day, releases relaxing spores"*
- *"Blue turtle with cannons on its shell"*
""")
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_pokemon = None
        st.rerun()

# Main PokeApp UI
st.markdown("📟 PokéDex AI")
st.caption("Describe any Pokémon and I'll identify it using live PokéAPI data!")

if st.session_state.last_pokemon:
    p = st.session_state.last_pokemon
    types_html = "".join(
        f'<span class="poke-type" style="background:{TYPE_COLORS.get(t, "#888")}">{t}</span>'
        for t in p.get("types", [])
    )
    col_img, col_info = st.columns([1, 3])
    with col_img:
        if p.get("sprite"):
            st.image(p["sprite"], width=120)
    with col_info:
        st.markdown(f'<div class="poke-name">#{p["id"]} {p["name"].upper()}</div>', unsafe_allow_html=True)
        st.markdown(types_html, unsafe_allow_html=True)
        stats = p.get("base_stats", {})
        if stats:
            st.caption(f"HP {stats.get('hp', '?')} · ATK {stats.get('attack', '?')} · DEF {stats.get('defense', '?')} · SPD {stats.get('speed', '?')}")

st.divider()

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        if msg.get("tool_calls"):
            for name, inp, _ in msg["tool_calls"]:
                st.markdown(f'<span class="tool-badge">🔧 pokeapi · {name}</span>', unsafe_allow_html=True)

user_input = st.chat_input("Describe a Pokémon… (e.g. 'blue turtle with cannons on its back')")
#takes user input, appends to its history, calls the selected agent, stores the response, 
#updates last_pokemon if it was found then re-runs the app to refresh the UI
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Validate the correct API key is present
    active_key = (st.session_state.anthropic_key if st.session_state.provider == "Anthropic"
                  else st.session_state.openai_key)
    if not active_key:
        st.error(f"🔑 Enter your {st.session_state.provider} API key in the sidebar.")
    else:
        try:
            with st.spinner("🔍 Searching the PokéDex…"):
                if st.session_state.provider == "Anthropic":
                    result = chat_with_claude(
                        api_key=active_key,
                        model=st.session_state.model,
                        max_tokens=st.session_state.max_tokens,
                        temperature=st.session_state.temperature,
                        messages=st.session_state.messages,
                    )
                else:
                    result = chat_with_openai(
                        api_key=active_key,
                        model=st.session_state.model,
                        max_tokens=st.session_state.max_tokens,
                        temperature=st.session_state.temperature,
                        messages=st.session_state.messages,
                    )

            if result:
                final_text, tool_calls, found_pokemon = result
                st.session_state.messages.append({
                    "role": "assistant", "content": final_text, "tool_calls": tool_calls,
                })
                if found_pokemon:
                    st.session_state.last_pokemon = found_pokemon

        except Exception as e:
            st.error(f"❌ Error: {e}")


    st.rerun()
