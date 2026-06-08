import textwrap
from html import escape
from html.parser import HTMLParser

import streamlit as st


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())

    def get_text(self):
        return " ".join(self.parts)


def _clean_text(value):
    text = "" if value is None else str(value)
    if "<" in text and ">" in text:
        parser = _TextExtractor()
        parser.feed(text)
        extracted = parser.get_text()
        if extracted:
            return extracted
    return text


def _html(value):
    return escape(_clean_text(value), quote=True)


def _render_html(html_str):
    # Programmatically strip all leading/trailing whitespaces from each line
    # to prevent Streamlit's markdown parser from rendering HTML as raw code blocks.
    clean_html = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(clean_html, unsafe_allow_html=True)


def render_complaint_card(c, submit_dt, res_dt, priority_style, status_style):
    landmark_html = (
        f"<span><b>Landmark:</b> {_html(c.get('landmark'))}</span>"
        if c.get("landmark")
        else ""
    )
    resolved_html = f"<span><b>Resolved:</b> {_html(res_dt)}</span>" if res_dt else ""

    card_html = f"""
        <div class="custom-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div>
                    <code style="font-size: 1rem; color: #38bdf8; font-weight: 700;">{_html(c.get('ticket_number'))}</code>
                    <span class="priority-pill priority-{_html(priority_style)}">{_html(c.get('priority'))} Priority</span>
                    <span class="status-pill status-progress" style="margin-left: 8px;">{_html(c.get('category'))}</span>
                </div>
                <span class="status-pill status-{_html(status_style)}">{_html(c.get('status'))}</span>
            </div>
            <p style="margin: 0.5rem 0; font-size: 1.05rem; color: #f1f5f9;">{_html(c.get('complaint_text'))}</p>
            <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; font-size: 0.85rem; color: #94a3b8; margin-top: 0.75rem;">
                <span><b>Locality:</b> {_html(c.get('locality'))}</span>
                <span><b>Address:</b> {_html(c.get('address'))}</span>
                {landmark_html}
                <span><b>Submitted:</b> {_html(submit_dt)}</span>
                {resolved_html}
            </div>
        </div>
    """
    _render_html(card_html)


def render_officer_complaint_card(c, submit_dt, res_dt, priority_style, status_style):
    landmark_html = (
        f"<span><b>Landmark:</b> {_html(c.get('landmark'))}</span>"
        if c.get("landmark")
        else ""
    )
    resolved_html = f"<span><b>Resolved:</b> {_html(res_dt)}</span>" if res_dt else ""

    card_html = f"""
        <div class="custom-card" style="border-left: 6px solid #ef4444; background: rgba(0,0,0,0.15); margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-weight: 700; color: #38bdf8; font-size: 1.1rem;">{_html(c.get('ticket_number'))}</span>
                <span class="status-pill status-{_html(status_style)}">{_html(c.get('status'))}</span>
            </div>
            <span class="priority-pill priority-{_html(priority_style)}" style="margin: 0 0 1rem 0;">{_html(c.get('priority'))} Priority</span>

            <p style="font-size: 1.05rem; color: #f8fafc; margin: 0.5rem 0 1rem 0;">{_html(c.get('complaint_text'))}</p>

            <div style="font-size: 0.85rem; color: #94a3b8; display: flex; flex-wrap: wrap; gap: 1.5rem;">
                <span><b>Locality:</b> {_html(c.get('locality'))}</span>
                <span><b>Address:</b> {_html(c.get('address'))}</span>
                {landmark_html}
                <span><b>Submitted On:</b> {_html(submit_dt)}</span>
                {resolved_html}
            </div>
        </div>
    """
    _render_html(card_html)


def render_ticket_tracker_details(c, submit_dt, res_dt, priority_style, status_style):
    landmark_html = (
        f"<div><b>Landmark:</b> {_html(c.get('landmark'))}</div>"
        if c.get("landmark")
        else ""
    )

    card_html = f"""
        <div class="custom-card" style="margin-top: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #ffffff;">Ticket Tracking Details</h4>
                <span class="status-pill status-{_html(status_style)}">{_html(c.get('status'))}</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; background: rgba(0,0,0,0.15); padding: 1rem; border-radius: 8px;">
                <div><b>Ticket Reference:</b> <code style="color: #38bdf8; font-size: 1.05rem;">{_html(c.get('ticket_number'))}</code></div>
                <div><b>Category:</b> <span class="status-pill status-progress" style="padding: 2px 10px;">{_html(c.get('category'))}</span></div>
                <div><b>Priority:</b> <span class="priority-pill priority-{_html(priority_style)}">{_html(c.get('priority'))} Priority</span></div>
                <div><b>Locality Office:</b> {_html(c.get('locality'))}</div>
                <div><b>Detailed Address:</b> {_html(c.get('address'))}</div>
                {landmark_html}
                <div><b>Submission Timestamp:</b> {_html(submit_dt)}</div>
                <div><b>Resolution Date:</b> {_html(res_dt)}</div>
            </div>

            <div style="margin-top: 1rem;">
                <p style="font-weight: 600; margin-bottom: 0.25rem;">Complaint Text Description:</p>
                <p style="padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 6px; border-left: 4px solid #0ea5e9;">{_html(c.get('complaint_text'))}</p>
            </div>
        </div>
    """
    _render_html(card_html)


def render_dashboard_metrics(summary):
    avg_rating = summary.get("average_rating", 0.0)
    avg_rating_text = "N/A" if avg_rating == 0 else f"{avg_rating} stars"
    metrics_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-label">Total Complaints</div>
                <div class="metric-value" style="color: #38bdf8;">{_html(summary.get('total_complaints', 0))}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Pending Complaints</div>
                <div class="metric-value" style="color: #fbbf24;">{_html(summary.get('pending_complaints', 0))}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Resolved Complaints</div>
                <div class="metric-value" style="color: #34d399;">{_html(summary.get('resolved_complaints', 0))}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">High Priority</div>
                <div class="metric-value" style="color: #ef4444;">{_html(summary.get('high_priority_complaints', 0))}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Avg Rating</div>
                <div class="metric-value" style="color: #eab308;">{_html(avg_rating_text)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Reopened</div>
                <div class="metric-value" style="color: #a855f7;">{_html(summary.get('reopened_complaints', 0))}</div>
            </div>
        </div>
    """
    _render_html(metrics_html)
