"""
Enhanced CSS Styles for Lumia Investment Advisor Components

This module contains all CSS styles for the enhanced UI components.
"""

def get_enhanced_css():
    """Return enhanced CSS for all components"""
    
    return """
    <style>
    /* Enhanced Base Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-color: #48bb78;
        --warning-color: #ffc107;
        --error-color: #f56565;
        --info-color: #4299e1;
        --text-primary: #e2e8f0;
        --text-secondary: #a0aec0;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --shadow-glow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Enhanced Header Styles */
    .enhanced-header {
        position: relative;
        padding: 4rem 2rem;
        text-align: center;
        margin-bottom: 3rem;
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.15) 0%, 
            rgba(118, 75, 162, 0.15) 50%, 
            rgba(240, 147, 251, 0.15) 100%);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        overflow: hidden;
    }
    
    .enhanced-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--primary-gradient);
    }
    
    .header-title {
        font-size: 4rem;
        font-weight: 800;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: -2px;
    }
    
    .header-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .header-decoration {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .decoration-line {
        width: 60px;
        height: 2px;
        background: var(--primary-gradient);
        border-radius: 1px;
    }
    
    .decoration-diamond {
        font-size: 1.5rem;
        animation: float 3s ease-in-out infinite;
    }
    
    /* Enhanced Metric Cards */
    .metric-card-enhanced {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-glow);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--primary-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card-enhanced:hover::before {
        transform: scaleX(1);
    }
    
    .metric-card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .metric-icon {
        font-size: 1.5rem;
        opacity: 0.8;
    }
    
    .metric-title {
        font-size: 0.95rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-change {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        background: rgba(72, 187, 120, 0.2);
        color: var(--success-color);
        display: inline-block;
    }
    
    .metric-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        filter: blur(30px);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
        transform: translate(-50%, -50%);
    }
    
    .metric-card-enhanced:hover .metric-glow {
        opacity: 0.3;
    }
    
    /* Enhanced Stock Cards */
    .stock-card-premium {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-glow);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .stock-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .stock-card-premium:hover::before {
        opacity: 0.05;
    }
    
    .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .stock-symbol-badge {
        background: var(--primary-gradient);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }
    
    .recommendation-badge-premium {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid currentColor;
    }
    
    .stock-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        line-height: 1.3;
    }
    
    .stock-sector-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    .price-section {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid var(--glass-border);
    }
    
    .price-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .price-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .price-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .target-price {
        color: var(--success-color);
    }
    
    .price-change {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    .price-change.positive {
        background: rgba(72, 187, 120, 0.2);
        color: var(--success-color);
    }
    
    .price-change.negative {
        background: rgba(245, 101, 101, 0.2);
        color: var(--error-color);
    }
    
    .change-icon {
        font-size: 1.2rem;
    }
    
    /* Risk Indicator */
    .risk-indicator {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid var(--glass-border);
    }
    
    .risk-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .risk-bars {
        display: flex;
        gap: 0.25rem;
        flex: 1;
    }
    
    .risk-bar {
        width: 8px;
        height: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    .risk-bar.active {
        background: var(--warning-color);
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
    }
    
    .risk-score {
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Stock Card Footer */
    .stock-card-footer {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--glass-border);
    }
    
    .stock-action-btn {
        flex: 1;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        backdrop-filter: blur(10px);
    }
    
    .stock-action-btn:hover {
        background: rgba(102, 126, 234, 0.2);
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    /* Progress Ring */
    .progress-ring-container {
        text-align: center;
        margin: 1rem 0;
    }
    
    .progress-ring-title {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .progress-ring-wrapper {
        position: relative;
        display: inline-block;
        margin: 0 auto;
    }
    
    .progress-ring {
        transform: rotate(-90deg);
    }
    
    .progress-ring-progress {
        transition: stroke-dashoffset 1s ease-in-out;
    }
    
    .progress-ring-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    .progress-percentage {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    /* Chat Interface Enhanced */
    .chat-interface-enhanced {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-glow);
        margin: 2rem 0;
        overflow: hidden;
    }
    
    .chat-header {
        display: flex;
        align-items: center;
        padding: 1.5rem 2rem;
        background: rgba(102, 126, 234, 0.1);
        border-bottom: 1px solid var(--glass-border);
    }
    
    .chat-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--primary-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-right: 1rem;
    }
    
    .chat-title h3 {
        margin: 0;
        color: var(--text-primary);
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    .chat-status {
        margin: 0.25rem 0 0 0;
        font-size: 0.85rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success-color);
        animation: pulse 2s infinite;
    }
    
    .chat-actions {
        margin-left: auto;
        display: flex;
        gap: 0.5rem;
    }
    
    .chat-action-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .chat-action-btn:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: scale(1.1);
    }
    
    /* Chat Messages */
    .chat-message-enhanced {
        display: flex;
        padding: 1.5rem 2rem;
        gap: 1rem;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .chat-message-enhanced:last-child {
        border-bottom: none;
    }
    
    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .ai-message .message-avatar {
        background: var(--primary-gradient);
    }
    
    .user-message .message-avatar {
        background: var(--secondary-gradient);
    }
    
    .message-content {
        flex: 1;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .message-sender {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    
    .message-timestamp {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }
    
    .message-text {
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* Dashboard Grid */
    .dashboard-grid {
        display: grid;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .dashboard-widget {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-glow);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .dashboard-widget:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
    }
    
    .widget-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .widget-icon {
        font-size: 1.5rem;
    }
    
    .widget-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 1.1rem;
    }
    
    .widget-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .widget-change {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        display: inline-block;
    }
    
    .widget-change.positive {
        background: rgba(72, 187, 120, 0.2);
        color: var(--success-color);
    }
    
    .widget-change.negative {
        background: rgba(245, 101, 101, 0.2);
        color: var(--error-color);
    }
    
    .widget-change.neutral {
        background: rgba(160, 174, 192, 0.2);
        color: var(--text-secondary);
    }
    
    /* Enhanced Animations */
    @keyframes animate-fade-in-down {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes animate-scale-in {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes animate-slide-in-left {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes animate-slide-in-right {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes animate-slide-in-up {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes animate-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes animate-progress {
        from {
            stroke-dashoffset: 283;
        }
        to {
            stroke-dashoffset: var(--progress-offset, 0);
        }
    }
    
    @keyframes animate-message-in {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        50% { text-shadow: 0 0 30px rgba(102, 126, 234, 0.8); }
    }
    
    /* Hover Effects */
    .hover-lift:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
    }
    
    .hover-transform:hover {
        transform: translateY(-5px) scale(1.02);
    }
    
    .glow-effect {
        animation: glow 3s ease-in-out infinite;
    }
    
    .glow-text {
        text-shadow: 0 0 20px currentColor;
    }
    
    /* Apply animations to components */
    .animate-fade-in-down { animation: animate-fade-in-down 0.8s ease-out; }
    .animate-scale-in { animation: animate-scale-in 0.6s ease-out; }
    .animate-slide-in-left { animation: animate-slide-in-left 0.7s ease-out; }
    .animate-slide-in-right { animation: animate-slide-in-right 0.7s ease-out; }
    .animate-slide-in-up { animation: animate-slide-in-up 0.8s ease-out; }
    .animate-fade-in { animation: animate-fade-in 0.6s ease-out; }
    .animate-fade-in-up { animation: animate-slide-in-up 0.8s ease-out; }
    .animate-message-in { animation: animate-message-in 0.5s ease-out; }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2.5rem;
        }
        
        .dashboard-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .stock-card-premium,
        .metric-card-enhanced {
            padding: 1.5rem;
        }
        
        .stock-card-footer {
            flex-direction: column;
        }
        
        .chat-header {
            padding: 1rem 1.5rem;
        }
        
        .chat-message-enhanced {
            padding: 1rem 1.5rem;
        }
    }
    
    /* Loading States */
    .loading-skeleton {
        animation: skeleton-loading 1.5s ease-in-out infinite;
    }
    
    @keyframes skeleton-loading {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 0.7; }
    }
    
    .skeleton-header,
    .skeleton-row,
    .skeleton-card {
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .skeleton-header { height: 40px; }
    .skeleton-row { height: 20px; }
    .skeleton-row.short { width: 60%; }
    .skeleton-card { height: 120px; }
    
    /* Toast Notifications */
    .toast-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: var(--shadow-glow);
        z-index: 1000;
        max-width: 400px;
    }
    
    .toast-icon {
        font-size: 1.2rem;
    }
    
    .toast-message {
        flex: 1;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .toast-close {
        cursor: pointer;
        color: var(--text-secondary);
        font-size: 1.2rem;
        padding: 0.25rem;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    .toast-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
    }
    </style>
    """