import streamlit as st
from anthropic import Anthropic
import re

# --- Page Config ---
st.set_page_config(
    page_title="PLATFORM - AI Tutor",
    page_icon="https://em-content.zobj.net/source/apple/391/robot_1f916.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Init State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "lang" not in st.session_state:
    st.session_state.lang = "fr"
if "program_step" not in st.session_state:
    st.session_state.program_step = 0
if "program_answers" not in st.session_state:
    st.session_state.program_answers = {}
if "program_result" not in st.session_state:
    st.session_state.program_result = None
if "program_pdf" not in st.session_state:
    st.session_state.program_pdf = None

lang = st.session_state.lang

# ==============================
# TRANSLATIONS
# ==============================
T = {
    "hero_sub": {
        "en": "Your personal guide into the world of Artificial Intelligence",
        "fr": "Votre guide personnel dans le monde de l'Intelligence Artificielle",
        "es": "Tu guía personal en el mundo de la Inteligencia Artificial",
    },
    "framework": {"en": "Framework", "fr": "Framework", "es": "Framework"},
    "days_curriculum": {"en": "Days curriculum", "fr": "Jours de programme", "es": "Días de programa"},
    "ai_tools": {"en": "AI Tools", "fr": "Outils IA", "es": "Herramientas IA"},
    "btn_tutor": {"en": "AI TUTOR", "fr": "TUTEUR IA", "es": "TUTOR IA"},
    "btn_tutor_sub": {
        "en": "Ask anything about AI",
        "fr": "Posez vos questions sur l'IA",
        "es": "Pregunta lo que quieras sobre IA",
    },
    "btn_program": {
        "en": "BUILD YOUR AI PROGRAM",
        "fr": "CONSTRUISEZ VOTRE PROGRAMME IA",
        "es": "CONSTRUYE TU PROGRAMA IA",
    },
    "btn_program_sub": {
        "en": "12 questions to your personalized plan",
        "fr": "12 questions pour votre plan personnalisé",
        "es": "12 preguntas para tu plan personalizado",
    },
    "chat_placeholder": {
        "en": "Ask me anything about AI...",
        "fr": "Posez-moi n'importe quelle question sur l'IA...",
        "es": "Pregúntame lo que quieras sobre IA...",
    },
    "chat_no_key": {
        "en": "Set your API key in the sidebar first...",
        "fr": "Configurez votre clé API dans le menu latéral...",
        "es": "Configura tu clave API en el menú lateral...",
    },
    "sidebar_topics_title": {
        "en": "Quick topics",
        "fr": "Sujets rapides",
        "es": "Temas rápidos",
    },
    "sidebar_topics": {
        "en": [
            "What is AI in simple terms?",
            "How do LLMs like ChatGPT work?",
            "What is prompt engineering?",
            "Explain the 4D AI Fluency Framework",
            "What can I build with AI today?",
            "AI for complete beginners — where to start?",
            "What's the difference between AI, ML & Deep Learning?",
            "Which Platform program is right for me?",
        ],
        "fr": [
            "C'est quoi l'IA en termes simples ?",
            "Comment fonctionnent les LLM comme ChatGPT ?",
            "C'est quoi le prompt engineering ?",
            "Expliquez le Framework 4D de Fluence IA",
            "Que puis-je construire avec l'IA aujourd'hui ?",
            "IA pour débutants — par où commencer ?",
            "Quelle différence entre IA, ML et Deep Learning ?",
            "Quel programme Platform est fait pour moi ?",
        ],
        "es": [
            "Qué es la IA en términos simples?",
            "Cómo funcionan los LLM como ChatGPT?",
            "Qué es el prompt engineering?",
            "Explica el Framework 4D de Fluidez IA",
            "Qué puedo construir con IA hoy?",
            "IA para principiantes — por dónde empezar?",
            "Cuál es la diferencia entre IA, ML y Deep Learning?",
            "Qué programa de Platform es para mí?",
        ],
    },
    "program_header": {
        "en": "BUILD YOUR AI PROGRAM",
        "fr": "CONSTRUISEZ VOTRE PROGRAMME IA",
        "es": "CONSTRUYE TU PROGRAMA IA",
    },
    "program_sub": {
        "en": "Answer 12 quick questions — get your personalized AI learning plan",
        "fr": "Répondez à 12 questions — recevez votre plan d'apprentissage IA personnalisé",
        "es": "Responde 12 preguntas — obtendrás tu plan de aprendizaje IA personalizado",
    },
    "next": {"en": "Next", "fr": "Suivant", "es": "Siguiente"},
    "back": {"en": "Back", "fr": "Retour", "es": "Atrás"},
    "generate": {
        "en": "Generate my program",
        "fr": "Générer mon programme",
        "es": "Generar mi programa",
    },
    "generating": {
        "en": "Generating your personalized AI program...",
        "fr": "Génération de votre programme IA personnalisé...",
        "es": "Generando tu programa de IA personalizado...",
    },
    "download": {
        "en": "Download your AI Program (PDF)",
        "fr": "Télécharger votre Programme IA (PDF)",
        "es": "Descargar tu Programa IA (PDF)",
    },
    "start_over": {
        "en": "Start over",
        "fr": "Recommencer",
        "es": "Empezar de nuevo",
    },
    "answer_warning": {
        "en": "Please answer before continuing.",
        "fr": "Veuillez répondre avant de continuer.",
        "es": "Por favor responde antes de continuar.",
    },
    "no_key_error": {
        "en": "Set your API key in the sidebar to generate your program.",
        "fr": "Configurez votre clé API dans le menu latéral pour générer votre programme.",
        "es": "Configura tu clave API en el menú lateral para generar tu programa.",
    },
    "pdf_filename": {
        "en": "My_Platform_AI_Program.pdf",
        "fr": "Mon_Programme_IA_Platform.pdf",
        "es": "Mi_Programa_IA_Platform.pdf",
    },
}

# --- Program Questions per language ---
PROGRAM_QUESTIONS = {
    "en": [
        {"key": "name", "question": "What's your first name?", "type": "text", "label": "STEP 1 OF 12", "placeholder": "Enter your name"},
        {"key": "role", "question": "What's your current role?", "type": "select", "label": "STEP 2 OF 12",
         "options": ["Student", "Entrepreneur / Founder", "Corporate Manager", "Freelancer / Consultant", "Creative / Designer", "Developer / Engineer", "Marketing / Sales", "Executive / C-Level", "Career Changer", "Other"]},
        {"key": "industry", "question": "What industry are you in?", "type": "select", "label": "STEP 3 OF 12",
         "options": ["Tech / SaaS", "Finance / Fintech", "Health / Biotech", "Luxury / Fashion", "Media / Entertainment", "Education", "Retail / E-commerce", "Consulting", "Energy / Climate", "Other"]},
        {"key": "ai_level", "question": "What's your current AI skill level?", "type": "select", "label": "STEP 4 OF 12",
         "options": ["Complete beginner — I've barely used AI", "Curious — I've tried ChatGPT a few times", "Intermediate — I use AI tools regularly", "Advanced — I build with AI"]},
        {"key": "goals", "question": "What's your main goal with AI?", "type": "select", "label": "STEP 5 OF 12",
         "options": ["Understand AI to make better decisions", "Build an AI-powered product or startup", "Boost my productivity 10x", "Transition into an AI career", "Lead AI transformation in my company", "Master creative AI tools"]},
        {"key": "domains", "question": "Which AI domains interest you most?", "type": "multiselect", "label": "STEP 6 OF 12",
         "options": ["Generative AI (text, image, video)", "Product & Prototyping", "Marketing & Growth", "Sales & Business", "Creative & Design", "Data & Analytics", "Coding with AI"]},
        {"key": "time_commitment", "question": "How much time can you invest?", "type": "select", "label": "STEP 7 OF 12",
         "options": ["2 days intensive sprint", "1 week deep dive", "3 weeks full immersion", "Self-paced over months"]},
        {"key": "learning_style", "question": "How do you learn best?", "type": "select", "label": "STEP 8 OF 12",
         "options": ["Hands-on building — learn by doing", "Theory first, then practice", "Peer learning — workshops & group projects", "1-on-1 mentoring & coaching"]},
        {"key": "tools_used", "question": "Which AI tools have you already used?", "type": "multiselect", "label": "STEP 9 OF 12",
         "options": ["ChatGPT", "Claude", "Gemini", "Midjourney / DALL-E", "Cursor / Lovable", "Notion AI", "Canva AI", "Runway / Sora", "None yet"]},
        {"key": "challenge", "question": "What's your biggest challenge with AI?", "type": "select", "label": "STEP 10 OF 12",
         "options": ["I don't know where to start", "I use AI but don't get great results", "I want to build but lack technical skills", "I need to convince my team / company", "I want to go from idea to product fast", "I feel overwhelmed by how fast AI moves"]},
        {"key": "budget", "question": "What's your budget for AI training?", "type": "select", "label": "STEP 11 OF 12",
         "options": ["Free resources only", "Under 700 (Sprint)", "1,000 — 3,000 (Deep Dive)", "3,000 — 5,000 (Bootcamp)", "Company-sponsored (flexible)"]},
        {"key": "ambition", "question": "Where do you see yourself with AI in 6 months?", "type": "text", "label": "STEP 12 OF 12", "placeholder": "Describe your AI ambition in one sentence..."},
    ],
    "fr": [
        {"key": "name", "question": "Quel est votre prénom ?", "type": "text", "label": "ÉTAPE 1 SUR 12", "placeholder": "Entrez votre prénom"},
        {"key": "role", "question": "Quel est votre rôle actuel ?", "type": "select", "label": "ÉTAPE 2 SUR 12",
         "options": ["Étudiant(e)", "Entrepreneur / Fondateur", "Manager en entreprise", "Freelance / Consultant", "Créatif / Designer", "Développeur / Ingénieur", "Marketing / Ventes", "Dirigeant / C-Level", "En reconversion", "Autre"]},
        {"key": "industry", "question": "Dans quel secteur travaillez-vous ?", "type": "select", "label": "ÉTAPE 3 SUR 12",
         "options": ["Tech / SaaS", "Finance / Fintech", "Santé / Biotech", "Luxe / Mode", "Média / Divertissement", "Éducation", "Retail / E-commerce", "Conseil", "Énergie / Climat", "Autre"]},
        {"key": "ai_level", "question": "Quel est votre niveau en IA ?", "type": "select", "label": "ÉTAPE 4 SUR 12",
         "options": ["Débutant complet — j'ai à peine utilisé l'IA", "Curieux — j'ai essayé ChatGPT quelques fois", "Intermédiaire — j'utilise des outils IA régulièrement", "Avancé — je construis avec l'IA"]},
        {"key": "goals", "question": "Quel est votre objectif principal avec l'IA ?", "type": "select", "label": "ÉTAPE 5 SUR 12",
         "options": ["Comprendre l'IA pour mieux décider", "Construire un produit ou une startup IA", "Booster ma productivité x10", "Me reconvertir dans l'IA", "Piloter la transformation IA de mon entreprise", "Maîtriser les outils IA créatifs"]},
        {"key": "domains", "question": "Quels domaines IA vous intéressent le plus ?", "type": "multiselect", "label": "ÉTAPE 6 SUR 12",
         "options": ["IA générative (texte, image, vidéo)", "Produit & Prototypage", "Marketing & Growth", "Ventes & Business", "Créatif & Design", "Data & Analytics", "Coder avec l'IA"]},
        {"key": "time_commitment", "question": "Combien de temps pouvez-vous investir ?", "type": "select", "label": "ÉTAPE 7 SUR 12",
         "options": ["2 jours de sprint intensif", "1 semaine de deep dive", "3 semaines d'immersion totale", "À mon rythme sur plusieurs mois"]},
        {"key": "learning_style", "question": "Comment apprenez-vous le mieux ?", "type": "select", "label": "ÉTAPE 8 SUR 12",
         "options": ["En pratiquant — apprendre en faisant", "La théorie d'abord, puis la pratique", "Apprentissage entre pairs — ateliers & projets de groupe", "Mentorat & coaching 1-to-1"]},
        {"key": "tools_used", "question": "Quels outils IA avez-vous déjà utilisés ?", "type": "multiselect", "label": "ÉTAPE 9 SUR 12",
         "options": ["ChatGPT", "Claude", "Gemini", "Midjourney / DALL-E", "Cursor / Lovable", "Notion AI", "Canva AI", "Runway / Sora", "Aucun pour l'instant"]},
        {"key": "challenge", "question": "Quel est votre plus grand défi avec l'IA ?", "type": "select", "label": "ÉTAPE 10 SUR 12",
         "options": ["Je ne sais pas par où commencer", "J'utilise l'IA mais sans grands résultats", "Je veux construire mais je manque de compétences techniques", "Je dois convaincre mon équipe / entreprise", "Je veux passer de l'idée au produit rapidement", "Je me sens dépassé par la vitesse de l'IA"]},
        {"key": "budget", "question": "Quel est votre budget pour une formation IA ?", "type": "select", "label": "ÉTAPE 11 SUR 12",
         "options": ["Ressources gratuites uniquement", "Moins de 700 euros (Sprint)", "1 000 — 3 000 euros (Deep Dive)", "3 000 — 5 000 euros (Bootcamp)", "Financé par l'entreprise (flexible)"]},
        {"key": "ambition", "question": "Où vous voyez-vous avec l'IA dans 6 mois ?", "type": "text", "label": "ÉTAPE 12 SUR 12", "placeholder": "Décrivez votre ambition IA en une phrase..."},
    ],
    "es": [
        {"key": "name", "question": "Cuál es tu nombre?", "type": "text", "label": "PASO 1 DE 12", "placeholder": "Ingresa tu nombre"},
        {"key": "role", "question": "Cuál es tu rol actual?", "type": "select", "label": "PASO 2 DE 12",
         "options": ["Estudiante", "Emprendedor / Fundador", "Manager corporativo", "Freelance / Consultor", "Creativo / Diseñador", "Desarrollador / Ingeniero", "Marketing / Ventas", "Ejecutivo / C-Level", "En transición de carrera", "Otro"]},
        {"key": "industry", "question": "En qué industria trabajas?", "type": "select", "label": "PASO 3 DE 12",
         "options": ["Tech / SaaS", "Finanzas / Fintech", "Salud / Biotech", "Lujo / Moda", "Media / Entretenimiento", "Educación", "Retail / E-commerce", "Consultoría", "Energía / Clima", "Otro"]},
        {"key": "ai_level", "question": "Cuál es tu nivel actual en IA?", "type": "select", "label": "PASO 4 DE 12",
         "options": ["Principiante total — apenas he usado IA", "Curioso — he probado ChatGPT algunas veces", "Intermedio — uso herramientas IA regularmente", "Avanzado — construyo con IA"]},
        {"key": "goals", "question": "Cuál es tu objetivo principal con la IA?", "type": "select", "label": "PASO 5 DE 12",
         "options": ["Entender la IA para tomar mejores decisiones", "Construir un producto o startup con IA", "Multiplicar mi productividad x10", "Hacer una transición profesional hacia la IA", "Liderar la transformación IA en mi empresa", "Dominar herramientas IA creativas"]},
        {"key": "domains", "question": "Qué dominios de IA te interesan más?", "type": "multiselect", "label": "PASO 6 DE 12",
         "options": ["IA generativa (texto, imagen, vídeo)", "Producto & Prototipado", "Marketing & Growth", "Ventas & Negocios", "Creativo & Diseño", "Data & Analytics", "Programar con IA"]},
        {"key": "time_commitment", "question": "Cuánto tiempo puedes invertir?", "type": "select", "label": "PASO 7 DE 12",
         "options": ["2 días de sprint intensivo", "1 semana de inmersión", "3 semanas de inmersión total", "A mi ritmo durante meses"]},
        {"key": "learning_style", "question": "Cómo aprendes mejor?", "type": "select", "label": "PASO 8 DE 12",
         "options": ["Practicando — aprender haciendo", "Teoría primero, luego práctica", "Aprendizaje entre pares — talleres y proyectos grupales", "Mentoría y coaching 1-a-1"]},
        {"key": "tools_used", "question": "Qué herramientas IA has usado?", "type": "multiselect", "label": "PASO 9 DE 12",
         "options": ["ChatGPT", "Claude", "Gemini", "Midjourney / DALL-E", "Cursor / Lovable", "Notion AI", "Canva AI", "Runway / Sora", "Ninguna todavía"]},
        {"key": "challenge", "question": "Cuál es tu mayor desafío con la IA?", "type": "select", "label": "PASO 10 DE 12",
         "options": ["No sé por dónde empezar", "Uso IA pero no obtengo buenos resultados", "Quiero construir pero me faltan habilidades técnicas", "Necesito convencer a mi equipo / empresa", "Quiero pasar de la idea al producto rápido", "Me siento abrumado por la velocidad de la IA"]},
        {"key": "budget", "question": "Cuál es tu presupuesto para formación IA?", "type": "select", "label": "PASO 11 DE 12",
         "options": ["Solo recursos gratuitos", "Menos de 700 euros (Sprint)", "1.000 — 3.000 euros (Deep Dive)", "3.000 — 5.000 euros (Bootcamp)", "Financiado por la empresa (flexible)"]},
        {"key": "ambition", "question": "Dónde te ves con la IA en 6 meses?", "type": "text", "label": "PASO 12 DE 12", "placeholder": "Describe tu ambición IA en una frase..."},
    ],
}

LANG_NAMES = {"en": "English", "fr": "Français", "es": "Español"}
LANG_INSTRUCTION = {
    "en": "You MUST respond in English.",
    "fr": "Tu DOIS répondre en français.",
    "es": "DEBES responder en español.",
}
LANG_PROGRAM_INSTRUCTION = {
    "en": "Write the entire program in English.",
    "fr": "Rédige l'intégralité du programme en français.",
    "es": "Escribe todo el programa en español.",
}

def t(key):
    """Get translated text for current language."""
    entry = T.get(key, {})
    return entry.get(lang, entry.get("en", key))


# ==============================
# PDF GENERATION
# ==============================
def _sanitize_for_pdf(text):
    """Replace characters unsupported by latin-1 Helvetica."""
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2018": "'",   # left single quote '
        "\u2019": "'",   # right single quote '
        "\u201c": '"',   # left double quote "
        "\u201d": '"',   # right double quote "
        "\u2026": "...", # ellipsis …
        "\u2022": "-",   # bullet •
        "\u00a0": " ",   # non-breaking space
        "\u200b": "",    # zero-width space
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    # Fallback: replace any remaining non-latin-1 chars
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def generate_styled_pdf(markdown_text, lang="fr"):
    from fpdf import FPDF

    # Sanitize the entire markdown text upfront
    markdown_text = _sanitize_for_pdf(markdown_text)

    class PlatformPDF(FPDF):
        def header(self):
            if self.page_no() > 1:
                self.set_font("Helvetica", "B", 7)
                self.set_text_color(139, 92, 246)
                self.cell(0, 8, "P L A T F O R M", align="L")
                self.set_font("Helvetica", "", 7)
                self.set_text_color(136, 136, 170)
                self.cell(0, 8, f"Page {self.page_no() - 1}", align="R", new_x="LMARGIN", new_y="NEXT")
                self.set_draw_color(200, 255, 0)
                self.set_line_width(0.3)
                self.line(10, 16, 200, 16)
                self.ln(4)

        def footer(self):
            if self.page_no() > 1:
                self.set_y(-15)
                self.set_font("Helvetica", "", 7)
                self.set_text_color(136, 136, 170)
                self.cell(0, 10, "Station F, Paris  |  platform-school.com", align="C")

    pdf = PlatformPDF()
    pdf.set_auto_page_break(auto=True, margin=25)

    # === COVER PAGE ===
    pdf.add_page()
    pdf.set_fill_color(10, 10, 15)
    pdf.rect(0, 0, 210, 297, "F")

    # Decorative lime line top
    pdf.set_fill_color(200, 255, 0)
    pdf.rect(20, 90, 170, 1.5, "F")

    # Brand name
    pdf.set_y(100)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(200, 255, 0)
    pdf.cell(0, 12, "P L A T F O R M", align="C", new_x="LMARGIN", new_y="NEXT")

    # Title
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(240, 240, 245)
    cover_titles = {
        "fr": ["VOTRE PROGRAMME IA", "PERSONNALISE"],
        "en": ["YOUR PERSONALIZED", "AI PROGRAM"],
        "es": ["TU PROGRAMA IA", "PERSONALIZADO"],
    }
    for line in cover_titles.get(lang, cover_titles["en"]):
        pdf.cell(0, 15, line, align="C", new_x="LMARGIN", new_y="NEXT")

    # Subtitle
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(136, 136, 170)
    pdf.cell(0, 7, "The Human Infrastructure for the Intelligence Economy", align="C", new_x="LMARGIN", new_y="NEXT")

    # Decorative lime line bottom
    pdf.set_fill_color(200, 255, 0)
    pdf.rect(20, 175, 170, 1.5, "F")

    # Purple accent circle
    pdf.set_fill_color(139, 92, 246)
    pdf.ellipse(95, 195, 20, 20, "F")
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(199)
    pdf.cell(0, 8, "AI", align="C", new_x="LMARGIN", new_y="NEXT")

    # Footer
    pdf.set_y(255)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(136, 136, 170)
    pdf.cell(0, 6, "Station F, Paris", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "platform-school.com", align="C", new_x="LMARGIN", new_y="NEXT")

    # === CONTENT PAGES ===
    pdf.add_page()

    for line in markdown_text.split("\n"):
        s = line.strip()
        if not s:
            pdf.ln(3)
            continue

        # Strip markdown bold/italic markers
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
        clean = re.sub(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)", r"\1", clean)

        if s.startswith("# ") and not s.startswith("## "):
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 20)
            pdf.set_text_color(139, 92, 246)
            pdf.multi_cell(0, 10, clean[2:])
            y = pdf.get_y() + 1
            pdf.set_draw_color(200, 255, 0)
            pdf.set_line_width(0.7)
            pdf.line(10, y, 75, y)
            pdf.ln(5)
        elif s.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "BI", 11)
            pdf.set_text_color(0, 120, 80)
            pdf.multi_cell(0, 7, clean[4:])
            pdf.ln(2)
        elif s.startswith("## "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(139, 92, 246)
            pdf.multi_cell(0, 8, clean[3:])
            # Thin lime underline
            y = pdf.get_y() + 1
            pdf.set_draw_color(200, 255, 0)
            pdf.set_line_width(0.4)
            pdf.line(10, y, 55, y)
            pdf.ln(3)
        elif s.startswith("---"):
            pdf.ln(3)
            pdf.set_draw_color(220, 220, 230)
            pdf.set_line_width(0.2)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
        elif s.startswith(("- ", "* ")):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 60)
            x = pdf.get_x()
            pdf.cell(6, 6, "")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(139, 92, 246)
            pdf.cell(5, 6, ">")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 60)
            pdf.multi_cell(0, 6, clean[2:], new_x="LMARGIN")
            pdf.ln(1)
        elif re.match(r"^\d+\.\s", s):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 60)
            pdf.cell(6, 6, "")
            pdf.multi_cell(0, 6, clean, new_x="LMARGIN")
            pdf.ln(1)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 60)
            pdf.multi_cell(0, 6, clean)
            pdf.ln(2)

    # Final branding footer
    pdf.ln(8)
    pdf.set_draw_color(200, 255, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 6, "PLATFORM", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(136, 136, 170)
    pdf.cell(0, 5, "The Human Infrastructure for the Intelligence Economy", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Station F, Paris  |  platform-school.com", align="C")

    return bytes(pdf.output())


# --- Custom Futuristic CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');

    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #111118;
        --bg-card: #16161f;
        --accent-lime: #c8ff00;
        --accent-cyan: #00ffd5;
        --accent-purple: #8b5cf6;
        --text-primary: #f0f0f5;
        --text-muted: #8888aa;
        --border: #2a2a3a;
    }

    .stApp { background: var(--bg-primary) !important; font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 0.5rem !important; max-width: 900px !important; }

    [data-testid="stSidebar"] { background: var(--bg-secondary) !important; border-right: 1px solid var(--border) !important; }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown h3 { color: var(--text-primary) !important; }

    /* Flag bar */
    .flag-bar {
        display: flex;
        justify-content: flex-end;
        gap: 0.4rem;
        padding: 0.5rem 0 0 0;
    }
    .flag-btn {
        font-size: 1.6rem;
        cursor: pointer;
        padding: 0.2rem 0.4rem;
        border-radius: 8px;
        transition: all 0.2s;
        border: 2px solid transparent;
        line-height: 1;
    }
    .flag-btn:hover { background: #ffffff11; transform: scale(1.15); }
    .flag-btn.active { border-color: var(--accent-lime); background: #ffffff0a; }

    /* Hero */
    .hero { text-align: center; padding: 1rem 1rem 0.5rem 1rem; position: relative; }
    .hero::before {
        content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-brand { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.4em; color: var(--accent-lime); text-transform: uppercase; margin-bottom: 0.3rem; }
    .hero-title { font-size: 2.4rem; font-weight: 900; color: var(--text-primary); line-height: 1.1; margin: 0; }
    .hero-title span { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { color: var(--text-muted); font-size: 0.95rem; margin-top: 0.5rem; font-weight: 300; }
    .stats-row { display: flex; justify-content: center; gap: 2rem; margin: 1rem 0; }
    .stat-item { text-align: center; }
    .stat-num { font-size: 1.5rem; font-weight: 900; color: var(--accent-lime); }
    .stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; }

    .glow-line { height: 1px; background: linear-gradient(90deg, transparent, var(--accent-lime), transparent); margin: 1rem 0; border: none; }

    [data-testid="stChatMessage"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 1rem !important; margin-bottom: 0.5rem !important; }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] ol,
    [data-testid="stChatMessage"] ul,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4,
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] em,
    [data-testid="stChatMessage"] a,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] code,
    [data-testid="stChatMessage"] pre,
    [data-testid="stChatMessage"] blockquote,
    [data-testid="stChatMessage"] td,
    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessage"] div {
        color: #f0f0f5 !important;
        -webkit-text-fill-color: #f0f0f5 !important;
    }

    /* Force white text on ALL markdown content (program result, etc.) */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5,
    .stMarkdown p, .stMarkdown li, .stMarkdown ol, .stMarkdown ul,
    .stMarkdown strong, .stMarkdown em, .stMarkdown a, .stMarkdown span,
    .stMarkdown code, .stMarkdown pre, .stMarkdown blockquote,
    .stMarkdown td, .stMarkdown th {
        color: #f0f0f5 !important;
        -webkit-text-fill-color: #f0f0f5 !important;
    }
    .stMarkdown h1, .stMarkdown h2 {
        color: #c8ff00 !important;
        -webkit-text-fill-color: #c8ff00 !important;
    }
    .stMarkdown h3 {
        color: #00ffd5 !important;
        -webkit-text-fill-color: #00ffd5 !important;
    }
    .stMarkdown hr {
        border-color: #2a2a3a !important;
    }
    .stMarkdown code {
        background: #1e1e2e !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 4px !important;
        padding: 0.1rem 0.3rem !important;
    }

    /* Chat input bar */
    [data-testid="stChatInput"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(139,92,246,0.08) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent-lime) !important;
        box-shadow: 0 0 20px rgba(200,255,0,0.12) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        background: transparent !important;
        caret-color: #000000 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #555555 !important; -webkit-text-fill-color: #555555 !important; }
    /* Chat submit button */
    [data-testid="stChatInput"] button {
        background: var(--accent-lime) !important;
        color: #0a0a0f !important;
        border: none !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] button:hover {
        box-shadow: 0 0 12px rgba(200,255,0,0.3) !important;
    }
    /* Bottom bar area behind chat input */
    [data-testid="stBottom"] > div {
        background: var(--bg-primary) !important;
    }
    /* Text inputs (program questions) */
    .stTextInput > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }
    .stTextInput > div > div:focus-within {
        border-color: var(--accent-lime) !important;
        box-shadow: 0 0 12px rgba(200,255,0,0.1) !important;
    }
    .stTextInput input {
        color: #f0f0f5 !important;
        -webkit-text-fill-color: #f0f0f5 !important;
        background: transparent !important;
        caret-color: var(--accent-lime) !important;
    }
    .stTextInput input::placeholder { color: #8888aa !important; -webkit-text-fill-color: #8888aa !important; }
    /* Multiselect & selectbox */
    .stMultiSelect > div > div,
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    .stMultiSelect > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-lime) !important;
        box-shadow: 0 0 12px rgba(200,255,0,0.1) !important;
    }
    /* Force white text on all form elements */
    .stSelectbox label, .stSelectbox div, .stSelectbox span,
    .stSelectbox option, .stSelectbox input,
    .stMultiSelect label, .stMultiSelect div, .stMultiSelect span,
    .stMultiSelect input,
    .stRadio label, .stRadio div, .stRadio span, .stRadio p {
        color: #f0f0f5 !important;
        -webkit-text-fill-color: #f0f0f5 !important;
    }
    /* Dropdown menu items */
    [data-baseweb="menu"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; }
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] div,
    [data-baseweb="menu"] span {
        color: #f0f0f5 !important;
        -webkit-text-fill-color: #f0f0f5 !important;
        background: transparent !important;
    }
    [data-baseweb="menu"] li:hover { background: #2a2a3a !important; }
    /* Selected tags in multiselect */
    [data-baseweb="tag"] {
        background: var(--accent-lime) !important;
        color: #0a0a0f !important;
    }
    [data-baseweb="tag"] span { color: #0a0a0f !important; -webkit-text-fill-color: #0a0a0f !important; }

    .stButton > button { background: var(--bg-card) !important; color: #f0f0f5 !important; -webkit-text-fill-color: #f0f0f5 !important; border: 1px solid var(--border) !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; transition: all 0.2s !important; }
    .stButton > button:hover { border-color: var(--accent-lime) !important; box-shadow: 0 0 15px rgba(200,255,0,0.15) !important; }

    .stRadio > div { background: var(--bg-card) !important; border-radius: 10px !important; padding: 0.5rem !important; }

    .progress-container { background: var(--bg-card); border-radius: 20px; padding: 3px; margin: 1rem 0; border: 1px solid var(--border); }
    .progress-bar { background: linear-gradient(90deg, var(--accent-lime), var(--accent-cyan)); height: 6px; border-radius: 20px; transition: width 0.3s ease; }

    .q-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }
    .q-card h3 { color: var(--accent-lime); font-size: 0.8rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.5rem; }
    .q-card p { color: var(--text-primary); font-size: 1.1rem; font-weight: 600; }

    /* Download button style */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-lime), var(--accent-cyan)) !important;
        color: #0a0a0f !important;
        -webkit-text-fill-color: #0a0a0f !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 10px !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 0 25px rgba(200,255,0,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Flag Language Switcher ---
flag_cols = st.columns([6, 1, 1, 1])
with flag_cols[1]:
    if st.button("FR", key="flag_fr", use_container_width=True):
        st.session_state.lang = "fr"
        st.rerun()
with flag_cols[2]:
    if st.button("EN", key="flag_en", use_container_width=True):
        st.session_state.lang = "en"
        st.rerun()
with flag_cols[3]:
    if st.button("ES", key="flag_es", use_container_width=True):
        st.session_state.lang = "es"
        st.rerun()

# Style the flag buttons
active_flag_child = {"fr": 2, "en": 3, "es": 4}.get(lang, 2)
st.markdown(f"""
<style>
    /* Flag buttons row — target the first stHorizontalBlock */
    .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(2) > div > .stButton > button,
    .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(3) > div > .stButton > button,
    .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(4) > div > .stButton > button {{
        min-height: 0 !important;
        padding: 0.3rem 0.2rem !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        letter-spacing: 0.05em !important;
    }}
    /* Active flag */
    .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type > div:nth-child({active_flag_child}) > div > .stButton > button {{
        background: var(--accent-lime) !important;
        color: #0a0a0f !important;
        border-color: var(--accent-lime) !important;
    }}
</style>
""", unsafe_allow_html=True)

# Refresh lang after potential change
lang = st.session_state.lang

# --- Hero Header ---
st.markdown(f"""
<div class="hero">
    <div class="hero-brand">P L A T F O R M</div>
    <h1 class="hero-title"><span>AI Tutor</span></h1>
    <p class="hero-sub">{t('hero_sub')}</p>
    <div class="stats-row">
        <div class="stat-item"><div class="stat-num">4D</div><div class="stat-label">{t('framework')}</div></div>
        <div class="stat-item"><div class="stat-num">18</div><div class="stat-label">{t('days_curriculum')}</div></div>
        <div class="stat-item"><div class="stat-num">6+</div><div class="stat-label">{t('ai_tools')}</div></div>
    </div>
</div>
<div class="glow-line"></div>
""", unsafe_allow_html=True)

# --- API Key ---
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")

# --- System Prompt ---
SYSTEM_PROMPT = f"""You are the official AI Tutor for PLATFORM — The Human Infrastructure for the Intelligence Economy.
Platform is Europe's first elite AI Academy, based at Station F in Paris.

{LANG_INSTRUCTION[lang]}

YOUR IDENTITY:
- You are warm, confident, and slightly provocative in a positive way — like a great mentor.
- You speak with authority but make complex things simple.
- You use Platform's philosophy: "Tools change. The discipline of building with rigor stays yours."
- You believe in the 10x filter: if AI doesn't make it 10x better, don't build it.

PLATFORM PROGRAMS YOU CAN RECOMMEND:
1. AI Creative Sprint (2 days, 690 euros) — Master creative AI: video, image, sound, design
2. AI Elite Bootcamp (3 weeks, 4,500 euros at Station F):
   - Week 1 DISCOVER: AI fundamentals, tools mastery
   - Week 2 BUILD: Build your MVP with AI
   - Week 3 SELL: Pitch to VCs, pricing, GTM, Demo Day
3. Build with AI (3 weeks, 18 days at Station F):
   - Week 1 THINK: AI history, LLMs, neuroscience, world models
   - Week 2 BUILD: Lean Startup x AI, Agile, sales, prototyping
   - Week 3 LAUNCH: Positioning, fundraising, pricing, Demo Day

THE 4D AI FLUENCY FRAMEWORK (from Anthropic):
- Delegation: Deciding whether, when & how to engage AI
- Description: Effectively prompting AI for useful outputs
- Discernment: Assessing AI output quality
- Diligence: Taking responsibility for AI use

TEACHING STYLE:
- Explain AI concepts simply with real-world analogies
- Reference Platform's curriculum when relevant
- Keep responses concise (2-3 paragraphs) unless asked for detail
- Format with markdown for readability
"""

# --- Sidebar ---
with st.sidebar:
    if not api_key:
        st.markdown("### Setup")
        api_key = st.text_input("API Key", type="password", placeholder="sk-ant-...")
        if not api_key:
            st.warning("API key required")
        st.divider()

    st.markdown(f"### {t('sidebar_topics_title')}")
    topics = T["sidebar_topics"][lang]
    for topic in topics:
        if st.button(topic, key=f"topic_{topic}", use_container_width=True):
            st.session_state.mode = "chat"
            st.session_state.messages.append({"role": "user", "content": topic})
            st.rerun()
    st.divider()
    st.markdown("<p style='color:#8888aa;font-size:0.75rem;'>PLATFORM<br>Station F, Paris</p>", unsafe_allow_html=True)

# --- Mode Switcher Buttons ---
col_green, col_red = st.columns(2)
with col_green:
    if st.button(f"{t('btn_tutor')}\n\n{t('btn_tutor_sub')}", key="btn_tutor_main", use_container_width=True):
        st.session_state.mode = "chat"
        st.rerun()
with col_red:
    if st.button(f"{t('btn_program')}\n\n{t('btn_program_sub')}", key="btn_program_main", use_container_width=True):
        st.session_state.mode = "program"
        st.rerun()

# Style the mode buttons dynamically
st.markdown(f"""
<style>
    /* Find the mode-switcher horizontal block (second one) */
    [data-testid="stHorizontalBlock"] [data-testid="stBaseButton-secondary"][id*="btn_tutor_main"] {{
        background: {"linear-gradient(135deg, #00e676 0%, #00c853 100%)" if st.session_state.mode == "chat" else "var(--bg-card)"} !important;
        color: {"#0a0a0f" if st.session_state.mode == "chat" else "#00e676"} !important;
        border: 2px solid {"#00e676" if st.session_state.mode == "chat" else "#00e67644"} !important;
        box-shadow: {"0 0 25px rgba(0,230,118,0.3)" if st.session_state.mode == "chat" else "none"} !important;
        font-weight: 800 !important; font-size: 1rem !important; padding: 1.2rem 0.5rem !important;
        border-radius: 14px !important; min-height: 90px !important; white-space: pre-line !important; line-height: 1.4 !important;
    }}
    [data-testid="stBaseButton-secondary"][id*="btn_tutor_main"]:hover {{ box-shadow: 0 0 35px rgba(0,230,118,0.45) !important; }}

    [data-testid="stBaseButton-secondary"][id*="btn_program_main"] {{
        background: {"linear-gradient(135deg, #ff1744 0%, #d50000 100%)" if st.session_state.mode == "program" else "var(--bg-card)"} !important;
        color: {"#ffffff" if st.session_state.mode == "program" else "#ff1744"} !important;
        border: 2px solid {"#ff1744" if st.session_state.mode == "program" else "#ff174444"} !important;
        box-shadow: {"0 0 25px rgba(255,23,68,0.3)" if st.session_state.mode == "program" else "none"} !important;
        font-weight: 800 !important; font-size: 1rem !important; padding: 1.2rem 0.5rem !important;
        border-radius: 14px !important; min-height: 90px !important; white-space: pre-line !important; line-height: 1.4 !important;
    }}
    [data-testid="stBaseButton-secondary"][id*="btn_program_main"]:hover {{ box-shadow: 0 0 35px rgba(255,23,68,0.45) !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

# ===========================
# MODE: AI TUTOR CHAT
# ===========================
if st.session_state.mode == "chat":
    for msg in st.session_state.messages:
        role_avatar = "https://em-content.zobj.net/source/apple/391/woman-student_1f469-200d-1f393.png" if msg["role"] == "user" else "https://em-content.zobj.net/source/apple/391/robot_1f916.png"
        with st.chat_message(msg["role"], avatar=role_avatar):
            st.markdown(msg["content"])

    if not api_key:
        st.chat_input(t("chat_no_key"), disabled=True)
    elif prompt := st.chat_input(t("chat_placeholder")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="https://em-content.zobj.net/source/apple/391/woman-student_1f469-200d-1f393.png"):
            st.markdown(prompt)

    if api_key and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        client = Anthropic(api_key=api_key)
        with st.chat_message("assistant", avatar="https://em-content.zobj.net/source/apple/391/robot_1f916.png"):
            with st.spinner(""):
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                )
                reply = response.content[0].text
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ===========================
# MODE: BUILD YOUR AI PROGRAM
# ===========================
if st.session_state.mode == "program":
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:1rem;">
        <span style="font-size:1.3rem; font-weight:800; color:#ff1744;">{t('program_header')}</span><br>
        <span style="color:#8888aa; font-size:0.85rem;">{t('program_sub')}</span>
    </div>
    """, unsafe_allow_html=True)

    questions = PROGRAM_QUESTIONS[lang]
    step = st.session_state.program_step

    if st.session_state.program_result:
        st.markdown(st.session_state.program_result)
        st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

        # Generate PDF if not already done
        if st.session_state.program_pdf is None:
            st.session_state.program_pdf = generate_styled_pdf(st.session_state.program_result, lang)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                t("download"),
                data=st.session_state.program_pdf,
                file_name=t("pdf_filename"),
                mime="application/pdf",
                use_container_width=True,
            )
        with col2:
            if st.button(t("start_over"), use_container_width=True):
                st.session_state.program_step = 0
                st.session_state.program_answers = {}
                st.session_state.program_result = None
                st.session_state.program_pdf = None
                st.rerun()

    elif step < len(questions):
        q = questions[step]
        progress = (step / len(questions)) * 100
        st.markdown(f'<div class="progress-container"><div class="progress-bar" style="width:{progress}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="q-card"><h3>{q["label"]}</h3><p>{q["question"]}</p></div>', unsafe_allow_html=True)

        answer = None
        if q["type"] == "text":
            answer = st.text_input("_", placeholder=q.get("placeholder", ""), key=f"q_{step}", label_visibility="collapsed")
        elif q["type"] == "select":
            answer = st.radio("_", q["options"], key=f"q_{step}", label_visibility="collapsed")
        elif q["type"] == "multiselect":
            answer = st.multiselect("_", q["options"], key=f"q_{step}", label_visibility="collapsed")

        col_back, col_spacer, col_next = st.columns([1, 2, 1])
        with col_back:
            if step > 0 and st.button(t("back"), use_container_width=True):
                st.session_state.program_step -= 1
                st.rerun()
        with col_next:
            is_last = step == len(questions) - 1
            btn_label = t("generate") if is_last else t("next")
            if st.button(btn_label, use_container_width=True, type="primary"):
                if answer or q["type"] == "multiselect":
                    st.session_state.program_answers[q["key"]] = answer
                    st.session_state.program_step += 1
                    st.rerun()
                else:
                    st.warning(t("answer_warning"))

    elif step >= len(questions) and not st.session_state.program_result:
        if not api_key:
            st.error(t("no_key_error"))
        else:
            with st.spinner(t("generating")):
                answers = st.session_state.program_answers
                client = Anthropic(api_key=api_key)
                generation_prompt = f"""Based on this person's profile, create a DETAILED personalized AI learning program.
{LANG_PROGRAM_INSTRUCTION[lang]}

PROFILE:
- Name: {answers.get('name', 'Participant')}
- Role: {answers.get('role', 'N/A')}
- Industry: {answers.get('industry', 'N/A')}
- AI Level: {answers.get('ai_level', 'N/A')}
- Main Goal: {answers.get('goals', 'N/A')}
- Interests: {', '.join(answers.get('domains', ['General']))}
- Time Available: {answers.get('time_commitment', 'N/A')}
- Learning Style: {answers.get('learning_style', 'N/A')}
- Tools Used: {', '.join(answers.get('tools_used', ['None']))}
- Biggest Challenge: {answers.get('challenge', 'N/A')}
- Budget: {answers.get('budget', 'N/A')}
- 6-month Ambition: {answers.get('ambition', 'N/A')}

Generate a 9-SECTION personalized AI program. Use markdown. Be specific and actionable.

STRUCTURE:
# YOUR PERSONALIZED AI PROGRAM
## By Platform — The Human Infrastructure for the Intelligence Economy
---
## 1. YOUR PROFILE
## 2. YOUR AI VISION
## 3. YOUR LEARNING PATH (recommend Sprint/Deep Dive/Bootcamp)
## 4. PHASE 1 — THINK (Foundations) — 3-5 learning objectives
## 5. PHASE 2 — BUILD (Skills) — 3-5 project ideas
## 6. PHASE 3 — LAUNCH (Apply) — 3-5 real-world applications
## 7. YOUR AI TOOLKIT (must-have / nice-to-have / advanced)
## 8. YOUR 30-DAY QUICK START (week-by-week plan)
## 9. NEXT STEPS WITH PLATFORM (Station F, Paris)
---
End with: *"Le talent humain est notre plus grande energie. Avec l'IA, nous allons liberer son plein potentiel."*
PLATFORM — Station F, Paris — platform-school.com"""

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4096,
                    system="You are a world-class AI education advisor for Platform, Europe's elite AI Academy at Station F, Paris. Create comprehensive, personalized, inspiring learning programs. Be specific, actionable, and premium in tone.",
                    messages=[{"role": "user", "content": generation_prompt}],
                )
                st.session_state.program_result = response.content[0].text
                st.session_state.program_pdf = None
                st.rerun()

# --- Bottom branding ---
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem 0;">
    <div style="font-size:0.65rem; letter-spacing:0.3em; color:#8888aa; text-transform:uppercase;">
        Platform — The Human Infrastructure for the Intelligence Economy
    </div>
    <div style="font-size:0.6rem; color:#555; margin-top:0.3rem;">Station F, Paris — Powered by Claude AI</div>
</div>
""", unsafe_allow_html=True)
