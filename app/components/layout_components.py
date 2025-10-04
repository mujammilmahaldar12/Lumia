"""
Layout Components for Lumia Investment Advisor

This module contains layout and structural components for better organization.
"""

import streamlit as st
from typing import List, Dict, Any, Optional

class LayoutComponents:
    """Layout and structural components"""
    
    @staticmethod
    def render_dashboard_grid(widgets: List[Dict[str, Any]], columns: int = 3):
        """Render responsive dashboard grid"""
        
        st.markdown('<div class="dashboard-grid animate-fade-in">', unsafe_allow_html=True)
        
        # Create columns
        cols = st.columns(columns)
        
        for i, widget in enumerate(widgets):
            col_index = i % columns
            with cols[col_index]:
                widget_type = widget.get('type', 'metric')
                
                if widget_type == 'metric':
                    st.markdown(f"""
                    <div class="dashboard-widget metric-widget animate-scale-in" 
                         style="animation-delay: {i * 0.1}s;">
                        <div class="widget-header">
                            <span class="widget-icon">{widget.get('icon', '📊')}</span>
                            <span class="widget-title">{widget.get('title', 'Metric')}</span>
                        </div>
                        <div class="widget-value">{widget.get('value', '0')}</div>
                        <div class="widget-change {widget.get('trend', 'neutral')}">{widget.get('change', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif widget_type == 'chart':
                    st.markdown(f"""
                    <div class="dashboard-widget chart-widget animate-slide-in-up" 
                         style="animation-delay: {i * 0.1}s;">
                        <div class="widget-header">
                            <span class="widget-title">{widget.get('title', 'Chart')}</span>
                        </div>
                        <div class="widget-content">
                            {widget.get('content', 'Chart placeholder')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_navigation(nav_items: List[Dict[str, str]], active_item: str = None):
        """Enhanced sidebar navigation"""
        
        st.markdown("""
        <div class="sidebar-nav animate-slide-in-left">
            <div class="nav-header">
                <div class="nav-logo">💎</div>
                <div class="nav-title">Lumia</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        selected_item = None
        for item in nav_items:
            is_active = item.get('key') == active_item
            active_class = 'active' if is_active else ''
            
            if st.button(
                f"{item.get('icon', '🔹')} {item.get('label', 'Item')}",
                key=item.get('key', 'nav_item'),
                help=item.get('description', ''),
                use_container_width=True
            ):
                selected_item = item.get('key')
        
        return selected_item
    
    @staticmethod
    def render_tabbed_interface(tabs: List[Dict[str, Any]], default_tab: int = 0):
        """Enhanced tabbed interface"""
        
        tab_names = [tab.get('title', f'Tab {i}') for i, tab in enumerate(tabs)]
        tab_objects = st.tabs(tab_names)
        
        for i, (tab_obj, tab_config) in enumerate(zip(tab_objects, tabs)):
            with tab_obj:
                st.markdown(f"""
                <div class="tab-content animate-fade-in" style="animation-delay: 0.2s;">
                    <div class="tab-header">
                        <h3>{tab_config.get('title', f'Tab {i}')}</h3>
                        <p>{tab_config.get('description', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render tab content
                content_func = tab_config.get('content_func')
                if content_func and callable(content_func):
                    content_func()
                else:
                    st.write(tab_config.get('content', 'Tab content'))
    
    @staticmethod
    def render_expandable_section(title: str, content: str, icon: str = "📋", 
                                 expanded: bool = False):
        """Enhanced expandable section"""
        
        with st.expander(f"{icon} {title}", expanded=expanded):
            st.markdown(f"""
            <div class="expandable-content animate-fade-in">
                {content}
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_status_banner(message: str, status: str = "info", dismissible: bool = True):
        """Status banner component"""
        
        status_configs = {
            "success": {"bg": "rgba(72, 187, 120, 0.1)", "border": "#48bb78", "icon": "✅"},
            "error": {"bg": "rgba(245, 101, 101, 0.1)", "border": "#f56565", "icon": "❌"},
            "warning": {"bg": "rgba(255, 193, 7, 0.1)", "border": "#ffc107", "icon": "⚠️"},
            "info": {"bg": "rgba(66, 153, 225, 0.1)", "border": "#4299e1", "icon": "ℹ️"}
        }
        
        config = status_configs.get(status, status_configs["info"])
        dismiss_btn = '<button class="banner-dismiss">×</button>' if dismissible else ''
        
        st.markdown(f"""
        <div class="status-banner {status} animate-slide-down" 
             style="background: {config['bg']}; border-left: 4px solid {config['border']};">
            <div class="banner-icon">{config['icon']}</div>
            <div class="banner-message">{message}</div>
            {dismiss_btn}
        </div>
        """, unsafe_allow_html=True)

class ResponsiveLayout:
    """Responsive layout utilities"""
    
    @staticmethod
    def create_responsive_columns(breakpoints: Dict[str, int]):
        """Create responsive columns based on screen size"""
        
        # Default to mobile-first approach
        cols = st.columns(breakpoints.get('mobile', 1))
        
        return cols
    
    @staticmethod
    def render_mobile_drawer():
        """Mobile drawer navigation"""
        
        if st.button("☰", key="mobile_menu", help="Open Menu"):
            st.markdown("""
            <div class="mobile-drawer animate-slide-in-left">
                <div class="drawer-header">
                    <h3>Menu</h3>
                    <button class="drawer-close">×</button>
                </div>
                <div class="drawer-content">
                    <!-- Navigation items will be rendered here -->
                </div>
            </div>
            <div class="drawer-overlay"></div>
            """, unsafe_allow_html=True)

# Export layout components
DashboardGrid = LayoutComponents.render_dashboard_grid
SidebarNavigation = LayoutComponents.render_sidebar_navigation
TabbedInterface = LayoutComponents.render_tabbed_interface
ExpandableSection = LayoutComponents.render_expandable_section
StatusBanner = LayoutComponents.render_status_banner
ResponsiveColumns = ResponsiveLayout.create_responsive_columns