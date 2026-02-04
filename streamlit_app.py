"""
Streamlit application for Fatwa RAG System.
A semantic search system for Islamic fatwas.
"""

import streamlit as st
from loguru import logger
import sys

# Configure page - must be first Streamlit command
st.set_page_config(
    page_title="البحث في الفتاوى",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import backend services
from app.config import settings
from app.services.supabase_service import supabase_service
from app.services.qdrant_service import qdrant_service
from app.layers.query_processor import query_processor
from app.layers.embedder import embedder
from app.layers.searcher import searcher
from app.layers.reranker import reranker
from app.layers.verifier import verifier
from app.layers.formatter import formatter

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")


def apply_custom_css():
    """Apply custom CSS for RTL and styling."""
    st.markdown("""
    <style>
        /* RTL Support */
        .stApp {
            direction: rtl;
        }

        /* Main container */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-radius: 20px;
            margin-bottom: 2rem;
        }

        .main-title {
            color: #166534;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .main-subtitle {
            color: #4d7c0f;
            font-size: 1.1rem;
        }

        /* Search box */
        .stTextInput > div > div > input {
            direction: rtl;
            text-align: right;
            font-size: 1.1rem;
            padding: 1rem;
            border-radius: 15px;
            border: 2px solid #86efac;
        }

        .stTextInput > div > div > input:focus {
            border-color: #22c55e;
            box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            padding: 0.75rem 2rem;
            border-radius: 12px;
            border: none;
            width: 100%;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        }

        /* Fatwa cards */
        .fatwa-card {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 2px solid #86efac;
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            direction: rtl;
            text-align: right;
        }

        .fatwa-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }

        .shaykh-name {
            color: #166534;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .series-name {
            color: #4d7c0f;
            font-size: 0.9rem;
        }

        .confidence-badge {
            background: white;
            color: #166534;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
        }

        .section-title {
            color: #166534;
            font-weight: bold;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .question-box {
            background: rgba(255, 255, 255, 0.5);
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            line-height: 1.8;
        }

        .summary-box {
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            border: 2px solid #6ee7b7;
            padding: 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            line-height: 1.8;
        }

        .answer-box {
            background: rgba(255, 255, 255, 0.5);
            padding: 1rem;
            border-radius: 12px;
            line-height: 1.8;
            white-space: pre-wrap;
        }

        /* Warning message */
        .warning-box {
            background: #fef3c7;
            border: 2px solid #fcd34d;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            color: #92400e;
            margin-bottom: 1rem;
        }

        /* No results */
        .no-results {
            background: #fef9c3;
            border: 2px solid #fde047;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Spinner */
        .stSpinner > div {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)


def display_fatwa_card(fatwa, index: int, is_best: bool = False):
    """Display a fatwa result card."""

    with st.container():
        # Header with shaykh name
        st.markdown(f"**الشيخ:** {fatwa.shaykh}")
        st.markdown(f"*السلسلة:* {fatwa.series}")

        st.divider()

        # Question
        st.markdown("**❓ السؤال:**")
        st.info(fatwa.question)

        # Summary (only for best result)
        if is_best and fatwa.summary:
            st.markdown("**📋 الخلاصة المركزة:**")
            st.success(fatwa.summary)

        # Full Answer
        with st.expander("📖 الجواب الكامل", expanded=not is_best or not fatwa.summary):
            st.markdown(fatwa.answer)

        # Source link
        if fatwa.link:
            st.markdown(f"[🔗 المصدر]({fatwa.link})")

        st.markdown("---")


def search_fatwas(query: str, limit: int = 5):
    """Execute the search pipeline."""
    try:
        # Layer 1: Process query
        processed_query = query_processor.process(query)

        # Layer 2: Embed query
        query_embedding = embedder.embed_query(processed_query)

        # Layer 3: Search in Qdrant
        search_results = searcher.search(
            query_vector=query_embedding,
            limit=settings.initial_search_limit,
            shaykh_filter=None
        )

        if not search_results:
            return None, "لم أجد نتائج في قاعدة البيانات"

        # Get full fatwa details from Supabase
        fatwa_ids = searcher.get_fatwa_ids(search_results)
        fatwas = supabase_service.get_fatwas_by_ids(fatwa_ids)

        if not fatwas:
            return None, "لم أجد الفتاوى في قاعدة البيانات"

        # Layer 4: Rerank
        ranked_fatwas = reranker.rerank(
            query=processed_query,
            fatwas=fatwas,
            top_k=limit * 2
        )

        if not ranked_fatwas:
            return None, "لم أجد نتائج مطابقة"

        # Layer 5: Verify
        top_score = ranked_fatwas[0][1]

        if not verifier.should_return_results(top_score):
            return None, "لم أجد فتوى تطابق سؤالك بدرجة كافية"

        # Filter
        filtered_fatwas = verifier.filter_results(
            ranked_fatwas,
            min_confidence=None
        )

        if not filtered_fatwas:
            return None, "النتائج الموجودة ذات صلة ضعيفة بسؤالك"

        # Layer 6: Format
        response = formatter.format_success_response(
            ranked_fatwas=filtered_fatwas,
            user_query=query,
            max_results=limit
        )

        return response, None

    except Exception as e:
        logger.error(f"Search error: {e}")
        return None, f"حدث خطأ أثناء البحث: {str(e)}"


def main():
    """Main Streamlit application."""

    # Apply custom CSS
    apply_custom_css()

    # Header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🕌 البحث في الفتاوى</div>
    </div>
    """, unsafe_allow_html=True)

    # Search input
    col1, col2, col3 = st.columns([1, 6, 1])

    with col2:
        query = st.text_input(
            "سؤالك",
            placeholder="اكتب سؤالك هنا...",
            label_visibility="collapsed"
        )

        search_clicked = st.button("🔍 ابحث", use_container_width=True)

    # Handle search
    if search_clicked and query:
        with st.spinner("جاري البحث في الفتاوى..."):
            response, error = search_fatwas(query, limit=5)

        if error:
            st.markdown(f"""
            <div class="no-results">
                <h3>⚠️ {error}</h3>
                <p>اقتراحات:</p>
                <ul style="text-align: right; direction: rtl;">
                    <li>حاول إعادة صياغة السؤال بطريقة مختلفة</li>
                    <li>استخدم كلمات أكثر وضوحاً</li>
                    <li>تأكد من أن السؤال يتعلق بأحكام شرعية</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        elif response and response.found:
            # Show warning if exists
            if response.message:
                st.warning(response.message)

            # Best result
            if response.fatwa:
                st.markdown("## 🏆 النتيجة الأفضل")
                display_fatwa_card(response.fatwa, 0, is_best=True)

            # Other results
            if response.other_results:
                st.markdown("## 📚 نتائج أخرى")
                for i, fatwa in enumerate(response.other_results):
                    display_fatwa_card(fatwa, i + 1, is_best=False)

    elif search_clicked and not query:
        st.warning("الرجاء كتابة سؤالك أولاً")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        نظام البحث الذكي في الفتاوى الشرعية
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
