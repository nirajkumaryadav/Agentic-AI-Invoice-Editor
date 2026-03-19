"""
AI Invoice Auditor Dashboard (Final Polished UI)
- Gradient background (light/dark)
- Dark Mode toggle
- Themed buttons, metrics, and tabs
- Clean, consistent UI (no functional changes)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import sys
import threading

# --- Imports ---
sys.path.append(str(Path(__file__).parent.parent))
from workflow.invoice_workflow import InvoiceAuditorWorkflow
from agents.monitor_agent import MonitorAgent

# --- Page Config ---
st.set_page_config(
    page_title="AI Invoice Auditor",
    page_icon="🤖",
    layout="wide"
)

# --- Custom Styles ---
def apply_custom_styles(dark_mode=False):
    """Inject theme-aware gradient background and UI styles."""
    bg_gradient = (
        "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)"
        if not dark_mode
        else "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
    )
    text_color = "#0f172a" if not dark_mode else "#f8fafc"
    card_bg = "rgba(255,255,255,0.85)" if not dark_mode else "rgba(30,41,59,0.85)"
    border_color = "#cbd5e1" if not dark_mode else "#334155"
    accent = "#2563eb" if not dark_mode else "#60a5fa"
    metric_bg = "rgba(226,232,240,0.6)" if not dark_mode else "rgba(51,65,85,0.6)"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
        }}
        .main {{
            padding: 1.5rem;
        }}
        /* Sidebar */
        div[data-testid="stSidebar"] {{
            background-color: {card_bg};
            border-right: 1px solid {border_color};
        }}
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(90deg, {accent} 0%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 0.6rem;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0.4,0,0.15);
        }}
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] button {{
            background: transparent;
            font-weight: 600 !important;
            border-bottom: 3px solid transparent;
        }}
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
            color: {accent} !important;
            border-bottom: 3px solid {accent};
        }}
        /* Metrics */
        div[data-testid="stMetricValue"] {{
            color: {text_color} !important;
        }}
        div[data-testid="stMetric"] {{
            background-color: {metric_bg};
            border-radius: 0.8rem;
            padding: 0.6rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        /* Expanders */
        .stExpander {{
            background-color: {card_bg} !important;
            border-radius: 0.8rem;
            border: 1px solid {border_color};
            padding: 0.2rem;
        }}
        /* Dataframe tweaks */
        div[data-testid="stDataFrame"] {{
            border-radius: 0.6rem;
            overflow: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Persistent Queue File ---
NEW_INVOICES_QUEUE = Path("./data/new_invoices_queue.json")

# --- Callback ---
def process_invoice_callback(file_path):
    """Add new invoice to queue file for Streamlit to pick up"""
    try:
        if NEW_INVOICES_QUEUE.exists():
            with open(NEW_INVOICES_QUEUE, 'r') as f:
                queue = json.load(f)
        else:
            queue = []
        if file_path not in queue:
            queue.append(file_path)
        NEW_INVOICES_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        with open(NEW_INVOICES_QUEUE, 'w') as f:
            json.dump(queue, f)
    except Exception as e:
        print(f"Error adding to queue: {e}")

# --- Initialize Workflow and Monitor ---
if 'workflow' not in st.session_state:
    st.session_state.workflow = InvoiceAuditorWorkflow()
    st.session_state.processed_results = []
    st.session_state.monitor = MonitorAgent(
        watch_path="./data/incoming",
        callback=process_invoice_callback
    )
    monitor_thread = threading.Thread(target=st.session_state.monitor.start, daemon=True)
    monitor_thread.start()
    st.session_state.monitor_started = True

# --- Header ---
st.title("📄 AI Invoice Auditor")
st.caption("Automated + Human-in-the-loop invoice validation system powered by Infosys & AWS Bedrock")
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Workflow Ready")

    if st.session_state.get('monitor_started'):
        st.success("📡 File Monitor Active")
        st.caption("📁 Watching: `./data/incoming/`")

    # Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    apply_custom_styles(dark_mode)

    # Process queue if present
    if NEW_INVOICES_QUEUE.exists():
        try:
            with open(NEW_INVOICES_QUEUE, 'r') as f:
                queue = json.load(f)
            if queue:
                for file_path in queue:
                    if Path(file_path).exists():
                        with st.spinner(f"Processing {Path(file_path).name}..."):
                            result = st.session_state.workflow.process_invoice(file_path)
                            st.session_state.processed_results.append(result)
                            st.session_state.current_result = result
                with open(NEW_INVOICES_QUEUE, 'w') as f:
                    json.dump([], f)
                st.success(f"✅ Processed {len(queue)} new invoice(s)!")
        except Exception as e:
            st.error(f"Error processing queue: {e}")

    # Metrics
    review_queue = st.session_state.workflow.get_review_queue()
    if review_queue:
        st.warning(f"⏸️ {len(review_queue)} awaiting review")

    rag_stats = st.session_state.workflow.get_rag_pipeline().get_stats()
    st.metric("Processed Invoices", rag_stats['total_documents'])
    st.metric("Indexed Chunks", rag_stats['total_chunks'])
    st.markdown("---")
    st.info("💡 Upload invoices or drop them into `data/incoming/`")


# Main content - four tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Vendor Email", "⏸️ Review Queue", "📊 Processed Invoices", "📋 Audit Reports"])

# TAB 1: Upload & Process
with tab1:
    st.header("Upload Invoice")
    
    uploaded_file = st.file_uploader(
        "Choose invoice file (PDF, DOCX, PNG)",
        type=['pdf', 'docx', 'png', 'jpg', 'jpeg']
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📄 File: {uploaded_file.name}")
        
        with col2:
            if st.button("🚀 Process", type="primary", use_container_width=True):
                # Save file
                upload_path = Path("./data/incoming") / uploaded_file.name
                upload_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(upload_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process through workflow
                with st.spinner("Processing through workflow..."):
                    result = st.session_state.workflow.process_invoice(str(upload_path))
                    st.session_state.processed_results.append(result)
                    st.session_state.current_result = result
                
                st.success("✅ Processing Complete!")
                st.rerun()
    
    # Show current result if available
    if 'current_result' in st.session_state and st.session_state.current_result:
        st.markdown("---")
        st.subheader("📋 Processing Results")
        
        result = st.session_state.current_result
        
        # Check if paused for review
        if result.get('status') == 'awaiting_human_review':
            st.warning("⏸️ **This invoice requires human review**")
            st.info("👉 Go to **'Review Queue'** tab to approve/reject and resume workflow")
            
            invoice_data = result.get('invoice_data', {})
            validation = result.get('validation_result', {})
            
            # Show basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Invoice No", invoice_data.get('invoice_no', 'N/A'))
            with col2:
                st.metric("Total", f"{invoice_data.get('currency', '')} {invoice_data.get('total_amount', 0)}")
            with col3:
                st.warning("⏸️ PAUSED")
            
            # Show discrepancies
            with st.expander("⚠️ Why it needs review:", expanded=True):
                for disc in validation.get('discrepancies', []):
                    st.warning(f"• {disc.get('message')}")
        
        else:
            # Normal completed workflow results
            invoice_data = result.get('invoice_data', {})
            validation = result.get('validation_result', {})
            
            # Basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Invoice No", invoice_data.get('invoice_no', 'N/A'))
            with col2:
                st.metric("Total", f"{invoice_data.get('currency', '')} {invoice_data.get('total_amount', 0)}")
            with col3:
                st.metric("Items", len(invoice_data.get('line_items', [])))
            with col4:
                rec = validation.get('recommendation', 'unknown').upper()
                
                # Show human verification badge if applicable
                if validation.get('human_override'):
                    st.success(f"✅ HUMAN VERIFIED")
                    st.caption(f"Decision: {rec}")
                elif rec == 'APPROVE':
                    st.success(f"✅ {rec}")
                elif rec == 'REJECT':
                    st.error(f"❌ {rec}")
                else:
                    st.warning(f"⚠️ {rec}")
            
            # Details in expander
            with st.expander("📄 Invoice Details", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Invoice Number:**", invoice_data.get('invoice_no', 'N/A'))
                    st.write("**PO Number:**", invoice_data.get('po_number', 'N/A'))
                    st.write("**Vendor:**", invoice_data.get('vendor_name', 'N/A'))
                with col2:
                    st.write("**Date:**", invoice_data.get('invoice_date', 'N/A'))
                    st.write("**Currency:**", invoice_data.get('currency', 'N/A'))
                    st.write("**Total:**", invoice_data.get('total_amount', 0))
                
                st.write("**Line Items:**")
                if invoice_data.get('line_items'):
                    items_df = pd.DataFrame(invoice_data['line_items'])
                    st.dataframe(items_df, use_container_width=True, hide_index=True)
            
            # Discrepancies
            with st.expander("⚠️ Validation Issues"):
                discrepancies = validation.get('discrepancies', [])
                if discrepancies:
                    for i, disc in enumerate(discrepancies, 1):
                        severity = disc.get('severity', 'info')
                        msg = f"**{i}. {disc.get('field')}:** {disc.get('message')}"
                        
                        if severity == 'error':
                            st.error(msg)
                        elif severity == 'warning':
                            st.warning(msg)
                        else:
                            st.info(msg)
                else:
                    st.success("✅ No validation issues")
            
            # Report
            with st.expander("📊 Audit Report"):
                # Show human verification if present
                if validation.get('human_override'):
                    st.success("✅ **HUMAN VERIFIED**")
                    human_override = validation['human_override']
                    st.info(f"**Human Decision:** {human_override.get('decision', 'N/A').upper()}")
                    st.info(f"**Reason:** {human_override.get('reason', 'No reason provided')}")
                    st.caption(f"Original: {human_override.get('original_recommendation', 'N/A').upper()} → Changed to: {human_override.get('decision', 'N/A').upper()}")
                    st.markdown("---")
                
                st.text_area("Report", result.get('report_text', ''), height=200, disabled=True)
            
            # RAG Summary
            with st.expander("🔍 RAG Summary"):
                st.write(result.get('rag_answer', 'No RAG summary available'))

# TAB 2: Review Queue
with tab2:
    st.header("⏸️ Invoices Awaiting Human Review")
    
    review_queue = st.session_state.workflow.get_review_queue()
    
    if review_queue:
        st.warning(f"⚠️ **{len(review_queue)} invoice(s) need human review to continue workflow**")
        st.markdown("---")
        
        for item in review_queue:
            state = item.get('state', {})
            invoice_data = state.get('invoice_data', {})
            validation = state.get('validation_result', {})
            invoice_no = invoice_data.get('invoice_no', 'Unknown')
            
            with st.expander(f"📄 **{invoice_no}** - Review Required", expanded=True):
                # Invoice details
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Invoice", invoice_no)
                with col2:
                    st.metric("Vendor", invoice_data.get('vendor_name', 'N/A'))
                with col3:
                    st.metric("Total", f"{invoice_data.get('currency', '')} {invoice_data.get('total_amount', 0)}")
                with col4:
                    st.metric("Items", len(invoice_data.get('line_items', [])))
                
                # Line items
                st.write("**Line Items:**")
                if invoice_data.get('line_items'):
                    items_df = pd.DataFrame(invoice_data['line_items'])
                    st.dataframe(items_df, use_container_width=True, hide_index=True)
                
                # Discrepancies
                st.write("**⚠️ Validation Issues (Why it needs review):**")
                discrepancies = validation.get('discrepancies', [])
                if discrepancies:
                    for disc in discrepancies:
                        severity = disc.get('severity', 'info')
                        if severity == 'error':
                            st.error(f"• [{severity.upper()}] {disc.get('message')}")
                        else:
                            st.warning(f"• [{severity.upper()}] {disc.get('message')}")
                else:
                    st.info("No specific discrepancies listed")
                
                st.markdown("---")
                st.subheader("🔧 Your Decision")
                
                # Human decision
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    decision = st.selectbox(
                        "Approve or Reject:",
                        ["approve", "reject"],
                        key=f"decision_{invoice_no}"
                    )
                    
                    reason = st.text_area(
                        "Reason for your decision:",
                        placeholder="Explain why you approve/reject this invoice...",
                        key=f"reason_{invoice_no}",
                        height=100
                    )
                
                with col2:
                    st.write("")
                    st.write("")
                    st.write("")
                    if st.button("✅ Submit & Resume Workflow", key=f"resume_{invoice_no}", type="primary", use_container_width=True):
                        if reason.strip():
                            # Update state with human decision
                            state['validation_result']['recommendation'] = decision
                            state['validation_result']['human_override'] = {
                                'decision': decision,
                                'reason': reason,
                                'original_recommendation': 'manual_review',
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Resume workflow
                            with st.spinner(f"▶️ Resuming workflow for {invoice_no}..."):
                                final_state = st.session_state.workflow.resume_workflow(state)
                                
                                # Add to processed results
                                st.session_state.processed_results.append(final_state)
                                
                                # Set as current result to display in Tab 1
                                st.session_state.current_result = final_state
                                
                                # Remove from queue
                                st.session_state.workflow.remove_from_review_queue(invoice_no)
                            
                            st.success(f"✅ Workflow resumed and completed for **{invoice_no}**")
                            st.info("📋 Go to 'Upload & Process' tab to see complete results")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning("⚠️ Please provide a reason for your decision")
    else:
        st.success("✅ **No invoices awaiting review**")
        st.info("Invoices are either auto-approved (if perfect) or sent here for manual review. Only humans can reject invoices.")

# TAB 3: Query Bot

with tab3:
    st.header("🤖 Invoice Query Assistant")
    st.caption("Ask questions about your processed invoices")
    
    # Get RAG stats to check if there's data
    rag_stats = st.session_state.workflow.get_rag_pipeline().get_stats()
    has_indexed_data = rag_stats['total_documents'] > 0
    
    if has_indexed_data:
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Indexed Invoices", rag_stats['total_documents'])
        with col2:
            st.metric("📑 Total Chunks", rag_stats['total_chunks'])
        with col3:
            if rag_stats.get('invoices'):
                approved_count = sum(1 for inv in rag_stats['invoices'] if inv.get('recommendation') == 'approve')
                st.metric("✅ Approved", approved_count)
        
        st.markdown("---")
        
        # Initialize chat history and pending query
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'pending_query' not in st.session_state:
            st.session_state.pending_query = None
        
        # Process pending query from button clicks
        if st.session_state.pending_query:
            query_to_process = st.session_state.pending_query
            st.session_state.pending_query = None
            
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': query_to_process
            })
            
            # Query RAG pipeline
            with st.spinner("🔍 Searching through invoices..."):
                rag_pipeline = st.session_state.workflow.get_rag_pipeline()
                result = rag_pipeline.query(query_to_process, evaluate=False)
            
            # Add assistant response
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': result['answer'],
                'sources': result.get('sources', [])
            })
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    with st.chat_message("user", avatar="👤"):
                        st.write(message['content'])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(message['content'])
                        if message.get('sources'):
                            with st.expander("📎 Sources"):
                                st.caption(", ".join(message['sources']))
        
        # Chat input
        user_query = st.chat_input("Ask about your invoices... (e.g., Which invoices were approved? Show me invoices from Acme Corp)")
        
        if user_query:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_query
            })
            
            # Query RAG pipeline
            with st.spinner("🔍 Searching through invoices..."):
                rag_pipeline = st.session_state.workflow.get_rag_pipeline()
                result = rag_pipeline.query(user_query, evaluate=False)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': result['answer'],
                'sources': result.get('sources', [])
            })
            
            # Rerun to update chat display
            st.rerun()
        
        # Suggested questions
        st.markdown("---")
        st.subheader("💡 Suggested Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Which invoices need manual review?", use_container_width=True):
                st.session_state.pending_query = "Which invoices need manual review?"
                st.rerun()
            
            if st.button("✅ Show me all approved invoices", use_container_width=True):
                st.session_state.pending_query = "Show me all approved invoices"
                st.rerun()
        
        with col2:
            if st.button("💰 What's the total amount of all invoices?", use_container_width=True):
                st.session_state.pending_query = "What's the total amount of all invoices?"
                st.rerun()
            
            if st.button("🏢 List all vendors", use_container_width=True):
                st.session_state.pending_query = "List all vendors from the invoices"
                st.rerun()
        
        # Clear chat button
        if st.session_state.chat_history:
            st.markdown("---")
            if st.button("🗑️ Clear Chat History", use_container_width=False):
                st.session_state.chat_history = []
                st.session_state.pending_query = None
                st.rerun()
    
    else:
        st.info("📭 No invoices indexed yet. Process some invoices first to start querying!")
        st.caption("Once you upload and process invoices, you'll be able to ask questions about them here.")


# TAB 4: Audit Reports
with tab4:
    st.header("📋 Audit Reports Archive")
    
    reports_path = Path("./outputs/reports")
    
    if reports_path.exists():
        # Get all JSON files
        report_files = sorted(list(reports_path.glob("*.json")), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if report_files:
            st.success(f"📁 Found {len(report_files)} audit report(s)")
            
            # Initialize session state for selected report
            if 'selected_report' not in st.session_state:
                st.session_state.selected_report = None
            
            # Reports list in sidebar-style column
            col_list, col_detail = st.columns([1, 2])
            
            with col_list:
                st.subheader("📑 Reports")
                
                for report_file in report_files:
                    try:
                        with open(report_file, 'r') as f:
                            report_data = json.load(f)
                        
                        invoice_summary = report_data.get('invoice_summary', {})
                        invoice_no = invoice_summary.get('invoice_no', 'Unknown')
                        vendor = invoice_summary.get('vendor_name', 'Unknown')
                        recommendation = report_data.get('recommendation', 'N/A').upper()
                        generated_at = report_data.get('generated_at', '')
                        
                        # Parse timestamp
                        if generated_at:
                            try:
                                dt = datetime.fromisoformat(generated_at)
                                date_str = dt.strftime("%b %d, %Y %H:%M")
                            except:
                                date_str = generated_at
                        else:
                            date_str = "Unknown date"
                        
                        # Color-coded button based on recommendation
                        if recommendation == 'APPROVE':
                            button_label = f"✅ {invoice_no}"
                        elif recommendation == 'REJECT':
                            button_label = f"❌ {invoice_no}"
                        else:
                            button_label = f"⚠️ {invoice_no}"
                        
                        if st.button(
                            f"{button_label}\n{vendor}\n{date_str}",
                            key=f"btn_{report_file.name}",
                            use_container_width=True
                        ):
                            st.session_state.selected_report = report_data
                
                    except Exception as e:
                        st.error(f"Error loading {report_file.name}: {e}")
            
            with col_detail:
                if st.session_state.selected_report:
                    report = st.session_state.selected_report
                    
                    st.subheader("📄 Report Details")
                    
                    # Header info
                    invoice_summary = report.get('invoice_summary', {})
                    human_verified = report.get('human_verified', False)
                    recommendation = report.get('recommendation', 'N/A').upper()
                    
                    # Status badge
                    if human_verified:
                        st.success("✅ HUMAN VERIFIED")
                    
                    # Metrics row
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Invoice No", invoice_summary.get('invoice_no', 'N/A'))
                    with col2:
                        st.metric("PO Number", invoice_summary.get('po_number', 'N/A'))
                    with col3:
                        amount = invoice_summary.get('total_amount', 0)
                        currency = invoice_summary.get('currency', '')
                        st.metric("Total", f"{currency} {amount}")
                    with col4:
                        if recommendation == 'APPROVE':
                            st.success(f"✅ {recommendation}")
                        elif recommendation == 'REJECT':
                            st.error(f"❌ {recommendation}")
                        else:
                            st.warning(f"⚠️ {recommendation}")
                    
                    st.markdown("---")
                    
                    # Vendor and date
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Vendor:**", invoice_summary.get('vendor_name', 'N/A'))
                    with col2:
                        generated_at = report.get('generated_at', 'N/A')
                        if generated_at != 'N/A':
                            try:
                                dt = datetime.fromisoformat(generated_at)
                                date_str = dt.strftime("%B %d, %Y at %H:%M:%S")
                            except:
                                date_str = generated_at
                        else:
                            date_str = generated_at
                        st.write("**Generated:**", date_str)
                    
                    # Discrepancies count
                    discrepancies_count = report.get('discrepancies_count', 0)
                    if discrepancies_count > 0:
                        st.warning(f"⚠️ **{discrepancies_count} discrepancy(ies) found**")
                    else:
                        st.success("✅ **No discrepancies found**")
                    
                    st.markdown("---")
                    
                    # Human override info
                    human_override = report.get('human_override')
                    if human_override:
                        with st.expander("👤 Human Override Details", expanded=True):
                            st.info(f"**Decision:** {human_override.get('decision', 'N/A').upper()}")
                            st.write(f"**Reason:** {human_override.get('reason', 'No reason provided')}")
                            original = human_override.get('original_recommendation', 'N/A')
                            st.caption(f"Original AI Recommendation: {original.upper()}")
                    
                    # Full audit report
                    with st.expander("📊 Full Audit Report", expanded=True):
                        report_text = report.get('report', 'No report text available')
                        st.markdown(report_text)
                    
                    # Invoice data details
                    with st.expander("📄 Invoice Data Details"):
                        full_data = report.get('full_data', {})
                        invoice_data = full_data.get('invoice_data', {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Invoice Date:**", invoice_data.get('invoice_date', 'N/A'))
                            st.write("**Currency:**", invoice_data.get('currency', 'N/A'))
                            st.write("**Subtotal:**", invoice_data.get('subtotal', 0))
                        with col2:
                            st.write("**Tax Amount:**", invoice_data.get('tax_amount', 0))
                            st.write("**Total Amount:**", invoice_data.get('total_amount', 0))
                            st.write("**Original Language:**", invoice_data.get('original_language', 'N/A'))
                        
                        # Line items
                        line_items = invoice_data.get('line_items', [])
                        if line_items:
                            st.write("**Line Items:**")
                            items_df = pd.DataFrame(line_items)
                            st.dataframe(items_df, use_container_width=True, hide_index=True)
                        
                        # Translation info
                        if invoice_data.get('was_translated'):
                            confidence = invoice_data.get('translation_confidence', 0)
                            st.info(f"🌐 Translated from {invoice_data.get('original_language', 'N/A')} (Confidence: {confidence:.2%})")
                    
                    # Validation details
                    with st.expander("🔍 Validation Details"):
                        validation = full_data.get('validation_result', {})
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if validation.get('data_validation_passed'):
                                st.success("✅ Data Validation")
                            else:
                                st.error("❌ Data Validation")
                        with col2:
                            if validation.get('business_validation_passed'):
                                st.success("✅ Business Validation")
                            else:
                                st.error("❌ Business Validation")
                        with col3:
                            erp_status = validation.get('erp_match_status', 'unknown')
                            if erp_status == 'match':
                                st.success(f"✅ ERP: {erp_status}")
                            else:
                                st.warning(f"⚠️ ERP: {erp_status}")
                        
                        # Discrepancies
                        discrepancies = validation.get('discrepancies', [])
                        if discrepancies:
                            st.write("**Discrepancies:**")
                            for disc in discrepancies:
                                severity = disc.get('severity', 'info')
                                msg = f"**{disc.get('field')}:** {disc.get('message')}"
                                if severity == 'error':
                                    st.error(msg)
                                elif severity == 'warning':
                                    st.warning(msg)
                                else:
                                    st.info(msg)
                        else:
                            st.success("✅ No discrepancies found")
                        
                        # Missing fields
                        missing_fields = validation.get('missing_fields', [])
                        if missing_fields:
                            st.warning(f"⚠️ **Missing fields:** {', '.join(missing_fields)}")
                    
                    # Raw JSON view
                    with st.expander("🔧 Raw JSON Data"):
                        st.json(report)
                
                else:
                    st.info("👈 Select a report from the list to view details")
        
        else:
            st.info("📭 No audit reports found in `outputs/reports/`")
            st.caption("Reports will appear here after processing invoices")
    
    else:
        st.warning("⚠️ Reports directory not found")
        st.caption("Expected path: `outputs/reports/`")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>🤖 AI Invoice Auditor | Powered by Infosys & AWS Bedrock</div>",
    unsafe_allow_html=True
)
