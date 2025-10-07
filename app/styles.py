"""
Reusable CSS Styles for Lumia Robo-Advisor
"""

def get_main_styles():
    """Get main application styles"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main container */
        .main {
            background-color: #f5f5f5 !important;
            padding: 0 !important;
        }
        
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 1600px !important;
            margin: 0 auto;
        }
        
        /* Header */
        .app-header {
            background: linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #3b82f6 100%);
            color: white;
            padding: 2rem 3rem;
            margin: -2rem -3rem 2.5rem -3rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-bottom: 4px solid #1e40af;
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
        }
        
        .app-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 500;
        }
        
        /* Section cards */
        .section-card {
            background: white !important;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Inputs */
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 2px solid #e5e7eb !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.9375rem !important;
            transition: all 0.2s !important;
        }
        
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus-within,
        .stTextInput > div > div > input:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }
        
        /* Button */
        .stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 0.875rem 2.5rem !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            transition: all 0.3s !important;
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(37, 99, 235, 0.4) !important;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .data-table th {
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            padding: 1rem 1.25rem;
            text-align: left;
            font-size: 0.8125rem;
            font-weight: 700;
            color: #374151;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid #e5e7eb;
        }
        
        .data-table td {
            padding: 1.25rem;
            border-bottom: 1px solid #e5e7eb;
            font-size: 0.9375rem;
            color: #111827 !important;
        }
        
        .data-table td * {
            color: #111827 !important;
        }
        
        .data-table td strong {
            color: #111827 !important;
            font-weight: 600;
        }
        
        .data-table tr:hover {
            background: #f9fafb;
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        /* Chat container */
        .chat-container {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 1.5rem;
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        }
        
        /* Streamlit overrides */
        .stApp {
            background-color: #f5f5f5 !important;
        }
        
        div[data-testid="stAppViewContainer"] {
            background-color: #f5f5f5 !important;
        }
        
        /* Remove padding between columns */
        [data-testid="column"] {
            padding: 0 0.5rem !important;
        }
        
        [data-testid="column"]:first-child {
            padding-left: 0 !important;
        }
        
        [data-testid="column"]:last-child {
            padding-right: 0 !important;
        }
        
        /* Success/Error alerts */
        .stSuccess, .stError, .stInfo, .stWarning {
            border-radius: 8px !important;
            padding: 1rem 1.25rem !important;
        }
    </style>
    """
