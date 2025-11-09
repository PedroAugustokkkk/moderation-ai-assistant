# --- Importações ---
import streamlit as st
import os
import re
from dotenv import load_dotenv
from sightengine.client import SightengineClient

# --- Configurações Globais ---
load_dotenv()

SIGHTENGINE_USER = os.getenv("SIGHTENGINE_USER")
SIGHTENGINE_SECRET = os.getenv("SIGHTENGINE_SECRET")

# --- 1. UI: Painel de Calibração (Admin) ---
# (Esta seção permanece inalterada)

st.set_page_config(page_title="SafeView AI", page_icon="🛡️")

st.sidebar.title("Painel de Calibração (Admin)")
st.sidebar.info("Ajuste a sensibilidade de cada modelo (Probabilidade 0.0 a 1.0).")

THRESHOLD_ADULT = st.sidebar.slider(
    "Nível de Bloqueio 'Adulto Explícito':",
    min_value=0.0, max_value=1.0, value=0.80, step=0.05
)
THRESHOLD_WEAPON = st.sidebar.slider(
    "Nível de Bloqueio 'Arma/Violência':",
    min_value=0.0, max_value=1.0, value=0.50, step=0.05
)
THRESHOLD_ALCOHOL = st.sidebar.slider(
    "Nível de Bloqueio 'Álcool':",
    min_value=0.0, max_value=1.0, value=0.90, step=0.05
)
THRESHOLD_DRUGS = st.sidebar.slider(
    "Nível de Bloqueio 'Drogas':",
    min_value=0.0, max_value=1.0, value=0.90, step=0.05
)
THRESHOLD_EMOTION = st.sidebar.slider(
    "Nível de Sinalização 'Emoção Negativa' (Rosto):",
    min_value=0.0, max_value=1.0, value=0.75, step=0.05
)

calibration_thresholds = {
    "adult": THRESHOLD_ADULT,
    "weapon": THRESHOLD_WEAPON,
    "alcohol": THRESHOLD_ALCOHOL,
    "drugs": THRESHOLD_DRUGS,
    "emotion": THRESHOLD_EMOTION
}

# --- 2. Lógica de Negócio (O "Moderador") ---
# (Esta função permanece inalterada)

@st.cache_data
def analyze_image_moderation(image_bytes: bytes, thresholds: dict) -> tuple[str, list, dict]:
    """
    Executa uma análise multi-feature (Nudez, WAD, OCR, Face) na imagem
    e retorna um veredito baseado nos thresholds calibrados.
    """
    try:
        client = SightengineClient(SIGHTENGINE_USER, SIGHTENGINE_SECRET)
        models_to_check = ['nudity-2.0', 'wad', 'text', 'face-attributes']
        output = client.check(*models_to_check).set_bytes(image_bytes)

        raw_response = output
        violations = [] 

        # --- Regra 1: Risco de Conteúdo (Nudity 2.0) ---
        nudity_data = output.get('nudity', {})
        score_adult = max(
            nudity_data.get('sexual_activity', 0.0),
            nudity_data.get('sexual_display', 0.0),
            nudity_data.get('erotica', 0.0)
        )
        if score_adult >= thresholds['adult']:
            violations.append(f"Conteúdo explícito (adulto) detectado (Score: {score_adult:.2f})")
            
        # --- Regra 2: Risco de Segurança (WAD - Leitura Plana) ---
        score_weapon = output.get('weapon', 0.0)
        if score_weapon >= thresholds['weapon']:
            violations.append(f"Risco de segurança (arma) detectado (Score: {score_weapon:.2f})")

        score_alcohol = output.get('alcohol', 0.0)
        if score_alcohol >= thresholds['alcohol']:
            violations.append(f"Conteúdo de álcool detectado (Score: {score_alcohol:.2f})")

        score_drugs = output.get('drugs', 0.0)
        if score_drugs >= thresholds['drugs']:
            violations.append(f"Conteúdo de drogas detectado (Score: {score_drugs:.2f})")
            
        # --- Regra 3: Risco de Negócio (Vazamento de Receita - OCR) ---
        # A chave 'content' só aparece se texto for encontrado
        detected_text = output.get('text', {}).get('content', '')
        text_lower = detected_text.lower()
        
        if ("whatsapp" in text_lower or "whats" in text_lower or 
            "@" in text_lower or re.search(r'\d{5,}', text_lower)):
            
            violations.append(f"Informações de contato (Telefone/@) detectadas na imagem: '{detected_text}'")
        
        # --- Regra 4: Risco Humano (Coerção - Face Attributes) ---
        faces = output.get('faces', [])
        if faces:
            face_attributes = faces[0].get('attributes', {})
            raw_response["debug_face_emotion"] = {
                "sorrow": face_attributes.get('sorrow', 0.0),
                "anger": face_attributes.get('anger', 0.0),
            }
            score_sorrow = face_attributes.get('sorrow', 0.0)
            score_anger = face_attributes.get('anger', 0.0)
            
            if (score_sorrow >= thresholds['emotion'] or 
                score_anger >= thresholds['emotion']):
                
                violations.append("RISCO HUMANO: Imagem sinalizada (emoção negativa detectada).")
        
        # --- Veredito Final ---
        if len(violations) > 0:
            return "REPROVADA (RISCO)", violations, raw_response
        else:
            return "APROVADA", ["A imagem está de acordo com as diretrizes."], raw_response

    except Exception as e:
        st.error(f"Erro ao contatar a API do Sightengine: {e}")
        return "ERRO", [f"Falha na análise: {e}"], {}

# --- 3. Interface Streamlit (UI - ATUALIZADA) ---
def main():
    st.title("🛡️ SafeView AI - Assistente de Risco (v4.1)")
    st.write("Protótipo de automação de moderação (Nudez + WAD + OCR + Face)")

    uploaded_file = st.file_uploader(
        "Faça o upload da foto de perfil para análise...",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        st.image(image_bytes, caption="Imagem Enviada para Análise", width=300)

        if st.button("Analisar Risco da Imagem"):
            with st.spinner("Analisando (Nudez + WAD + OCR + Face)..."):
                
                status, mensagens, raw_data = analyze_image_moderation(
                    image_bytes, 
                    calibration_thresholds
                )

                if status.startswith("APROVADA"):
                    st.success(f"**Status: {status}**")
                    st.info(f"**Justificativa:** {mensagens[0]}")
                elif status.startswith("REPROVADA"):
                    st.error(f"**Status: {status}**")
                    
                    st.write("**Justificativas (Violações Detectadas):**")
                    for msg in mensagens:
                        st.markdown(f"- {msg}")
                else:
                    st.warning(f"**Status: {status}**")
                
                # --- INÍCIO DA MUDANÇA (v4.1) ---
                st.subheader("Relatório de Análise de Texto (OCR)")
                
                # Extrai o texto do raw_data para exibição clara
                detected_text = raw_data.get('text', {}).get('content', '')

                if detected_text:
                    st.info(f"**Texto Detectado na Imagem:**\n> {detected_text}")
                else:
                    # Isso é o que você queria: confirmação de que o OCR rodou e não achou nada
                    st.info("**Texto Detectado na Imagem:** Nenhum texto encontrado.")
                # --- FIM DA MUDANÇA (v4.1) ---

                with st.expander("Ver resposta completa da API (JSON)"):
                    st.json(raw_data)

# --- Ponto de Entrada ---
if __name__ == "__main__":
    if not SIGHTENGINE_USER or not SIGHTENGINE_SECRET:
        st.error("Credenciais SIGHTENGINE_USER ou SIGHTENGINE_SECRET não encontradas no .env.")
    else:
        main()