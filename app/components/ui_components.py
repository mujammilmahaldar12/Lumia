"""
Advanced UI Components for Lumia Investment Advisor

This module contains reusable UI components with enhanced styling and animations.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional

class UIComponents:
    """Main UI Components class with advanced styling and animations"""
    
    @staticmethod
    def render_enhanced_header(title: str, subtitle: str, background_gradient: bool = True):
        """Enhanced header with gradient background and animations"""
        
        gradient_bg = """
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.15) 0%, 
            rgba(118, 75, 162, 0.15) 50%, 
            rgba(240, 147, 251, 0.15) 100%);
        """ if background_gradient else ""
        
        st.markdown(f"""
        <div class="enhanced-header animate-fade-in-down">
            <div class="header-background" style="{gradient_bg}"></div>
            <div class="header-content">
                <h1 class="header-title glow-effect">{title}</h1>
                <p class="header-subtitle typewriter-effect">{subtitle}</p>
                <div class="header-decoration">
                    <div class="decoration-line"></div>
                    <div class="decoration-diamond">💎</div>
                    <div class="decoration-line"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card_enhanced(title: str, value: str, change: str = None, 
                                  icon: str = None, color_scheme: str = "primary"):
        """Enhanced metric card with animations and better styling"""
        
        color_schemes = {
            "primary": {"bg": "rgba(102, 126, 234, 0.08)", "accent": "#667eea", "glow": "rgba(102, 126, 234, 0.3)"},
            "success": {"bg": "rgba(72, 187, 120, 0.08)", "accent": "#48bb78", "glow": "rgba(72, 187, 120, 0.3)"},
            "warning": {"bg": "rgba(245, 101, 101, 0.08)", "accent": "#f56565", "glow": "rgba(245, 101, 101, 0.3)"},
            "info": {"bg": "rgba(66, 153, 225, 0.08)", "accent": "#4299e1", "glow": "rgba(66, 153, 225, 0.3)"}
        }
        
        scheme = color_schemes.get(color_scheme, color_schemes["primary"])
        change_html = f'<div class="metric-change">{change}</div>' if change else ""
        icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ""
        
        st.markdown(f"""
        <div class="metric-card-enhanced animate-scale-in hover-lift" 
             style="background: {scheme['bg']}; border-left: 4px solid {scheme['accent']};">
            <div class="metric-card-header">
                {icon_html}
                <div class="metric-title">{title}</div>
            </div>
            <div class="metric-value glow-text" style="color: {scheme['accent']};">{value}</div>
            {change_html}
            <div class="metric-glow" style="background: {scheme['glow']};"></div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_stock_card_premium(stock_data: Dict[str, Any]):
        """Premium stock card with advanced styling and interactive elements"""
        
        recommendation_colors = {
            "BUY": {"bg": "rgba(72, 187, 120, 0.2)", "color": "#48bb78", "glow": "rgba(72, 187, 120, 0.4)"},
            "HOLD": {"bg": "rgba(255, 193, 7, 0.2)", "color": "#ffc107", "glow": "rgba(255, 193, 7, 0.4)"},
            "SELL": {"bg": "rgba(245, 101, 101, 0.2)", "color": "#f56565", "glow": "rgba(245, 101, 101, 0.4)"}
        }
        
        rec_style = recommendation_colors.get(stock_data.get('recommendation', 'HOLD'))
        price_change = ((stock_data.get('target_price', 0) / stock_data.get('current_price', 1)) - 1) * 100
        
        st.markdown(f"""
        <div class="stock-card-premium animate-slide-in-left hover-transform">
            <div class="stock-header">
                <div class="stock-symbol-badge">{stock_data.get('symbol', 'N/A')}</div>
                <div class="recommendation-badge-premium" 
                     style="background: {rec_style['bg']}; color: {rec_style['color']}; 
                            box-shadow: 0 0 20px {rec_style['glow']};">
                    {stock_data.get('recommendation', 'HOLD')}
                </div>
            </div>
            
            <h3 class="stock-name">{stock_data.get('name', 'Unknown Company')}</h3>
            
            <div class="stock-sector-tag">
                <span class="sector-icon">🏢</span>
                {stock_data.get('sector', 'General')}
            </div>
            
            <div class="price-section">
                <div class="price-row">
                    <span class="price-label">Current</span>
                    <span class="price-value">₹{stock_data.get('current_price', 0):.2f}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Target</span>
                    <span class="price-value target-price">₹{stock_data.get('target_price', 0):.2f}</span>
                </div>
                <div class="price-change {'positive' if price_change > 0 else 'negative'}">
                    <span class="change-icon">{'↗' if price_change > 0 else '↘'}</span>
                    {price_change:.1f}% Potential
                </div>
            </div>
            
            <div class="risk-indicator">
                <span class="risk-label">Risk Score</span>
                <div class="risk-bars">
                    {''.join(f'<div class="risk-bar {"active" if i < stock_data.get("risk_score", 0) else ""}" data-risk="{i+1}"></div>' for i in range(5))}
                </div>
                <span class="risk-score">{stock_data.get('risk_score', 0):.1f}/5</span>
            </div>
            
            <div class="stock-card-footer">
                <button class="stock-action-btn">📊 Analyze</button>
                <button class="stock-action-btn">⭐ Watch</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_ring(percentage: float, title: str, color: str = "#667eea", size: int = 120):
        """Animated circular progress ring"""
        
        circumference = 2 * 3.14159 * 45  # radius = 45
        stroke_offset = circumference - (percentage / 100) * circumference
        
        st.markdown(f"""
        <div class="progress-ring-container animate-fade-in">
            <div class="progress-ring-title">{title}</div>
            <div class="progress-ring-wrapper" style="width: {size}px; height: {size}px;">
                <svg class="progress-ring" width="{size}" height="{size}">
                    <circle class="progress-ring-background" 
                            cx="{size//2}" cy="{size//2}" r="45"
                            stroke="rgba(255,255,255,0.1)" stroke-width="8" fill="transparent"/>
                    <circle class="progress-ring-progress animate-progress" 
                            cx="{size//2}" cy="{size//2}" r="45"
                            stroke="{color}" stroke-width="8" fill="transparent"
                            stroke-dasharray="{circumference}"
                            stroke-dashoffset="{stroke_offset}"
                            stroke-linecap="round"/>
                </svg>
                <div class="progress-ring-text">
                    <span class="progress-percentage">{percentage:.1f}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_loading_skeleton():
        """Loading skeleton animation for better UX"""
        
        st.markdown("""
        <div class="loading-skeleton">
            <div class="skeleton-header"></div>
            <div class="skeleton-row"></div>
            <div class="skeleton-row short"></div>
            <div class="skeleton-row"></div>
            <div class="skeleton-card-grid">
                <div class="skeleton-card"></div>
                <div class="skeleton-card"></div>
                <div class="skeleton-card"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_notification_toast(message: str, type: str = "info", duration: int = 3000):
        """Animated notification toast"""
        
        icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        colors = {
            "success": {"bg": "rgba(72, 187, 120, 0.9)", "border": "#48bb78"},
            "error": {"bg": "rgba(245, 101, 101, 0.9)", "border": "#f56565"},
            "warning": {"bg": "rgba(255, 193, 7, 0.9)", "border": "#ffc107"},
            "info": {"bg": "rgba(66, 153, 225, 0.9)", "border": "#4299e1"}
        }
        
        style = colors.get(type, colors["info"])
        
        st.markdown(f"""
        <div class="toast-notification animate-slide-in-right" 
             style="background: {style['bg']}; border-left: 4px solid {style['border']};"
             data-duration="{duration}">
            <div class="toast-icon">{icons.get(type, icons['info'])}</div>
            <div class="toast-message">{message}</div>
            <div class="toast-close">×</div>
        </div>
        """, unsafe_allow_html=True)

class ChatInterface:
    """Enhanced chat interface with better UX"""
    
    @staticmethod
    def render_chat_container():
        """Render enhanced chat container"""
        
        st.markdown("""
        <div class="chat-interface-enhanced animate-fade-in-up">
            <div class="chat-header">
                <div class="chat-avatar">🤖</div>
                <div class="chat-title">
                    <h3>AI Investment Assistant</h3>
                    <p class="chat-status">
                        <span class="status-indicator online"></span>
                        Online & Ready to Help
                    </p>
                </div>
                <div class="chat-actions">
                    <button class="chat-action-btn" title="Settings">⚙️</button>
                    <button class="chat-action-btn" title="History">📝</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_chat_message(message: str, is_ai: bool = True, timestamp: str = None):
        """Render enhanced chat message"""
        
        message_class = "ai-message" if is_ai else "user-message"
        avatar = "🤖" if is_ai else "👤"
        sender = "AI Assistant" if is_ai else "You"
        
        st.markdown(f"""
        <div class="chat-message-enhanced {message_class} animate-message-in">
            <div class="message-avatar">{avatar}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">{sender}</span>
                    {f'<span class="message-timestamp">{timestamp}</span>' if timestamp else ''}
                </div>
                <div class="message-text">{message}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_quick_actions(actions: List[Dict[str, str]]):
        """Render quick action buttons for chat"""
        
        st.markdown('<div class="quick-actions-container">', unsafe_allow_html=True)
        
        cols = st.columns(len(actions))
        for i, action in enumerate(actions):
            with cols[i]:
                if st.button(f"{action.get('icon', '🔹')} {action.get('label', 'Action')}", 
                           key=f"quick_action_{i}",
                           help=action.get('description', '')):
                    return action.get('value')
        
        st.markdown('</div>', unsafe_allow_html=True)
        return None

# Export components
MetricCard = UIComponents.render_metric_card_enhanced
StockCard = UIComponents.render_stock_card_premium
ProgressRing = UIComponents.render_progress_ring
LoadingSkeleton = UIComponents.render_loading_skeleton
NotificationToast = UIComponents.render_notification_toast
ChatContainer = ChatInterface.render_chat_container
ChatMessage = ChatInterface.render_chat_message
QuickActions = ChatInterface.render_quick_actions