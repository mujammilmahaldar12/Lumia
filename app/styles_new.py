"""
Enhanced Modern Styles for Lumia Robo-Advisor
"""

def get_main_styles():
    """Get main application styles with modern UI"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
        
        /* Global Styles */
        .stApp {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        body, p, div, span, label, input, select, textarea {
            color: #111827 !important;
        }
        
        .main {
            background: transparent !important;
            padding: 0 !important;
        }
        
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 1600px !important;
            margin: 0 auto;
        }
        
        /* Enhanced App Header */
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4rem 3rem;
            margin: -2rem -3rem 3rem -3rem;
            border-radius: 0 0 40px 40px;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
            text-align: center;
        }
        
        .app-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 4rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            position: relative;
            z-index: 1;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .app-header p {
            margin: 1rem 0 0 0;
            font-size: 1.5rem;
            font-weight: 400;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }
        
        /* Enhanced Section Cards */
        .section-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2.5rem;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
        }
        
        /* Enhanced Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06d6a0);
            border-radius: 20px 20px 0 0;
        }
        
        .metric-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }
        
        .metric-value {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }
        
        .metric-delta {
            font-size: 0.9rem;
            font-weight: 700;
            margin-top: 0.5rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            display: inline-block;
        }
        
        /* Enhanced Section Headers */
        .section-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            position: relative;
        }
        
        .section-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            border-radius: 2px;
        }
        
        .section-subtitle {
            color: #6b7280;
            font-size: 1.1rem;
            margin-top: -1rem;
            margin-bottom: 2rem;
            font-weight: 500;
        }
        
        /* Enhanced Data Table */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1.5rem;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .data-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 1rem;
            text-align: left;
            font-weight: 600;
            color: white;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        
        .data-table td {
            padding: 1.5rem 1rem;
            border-bottom: 1px solid #f3f4f6;
            color: #374151;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .data-table tr:hover {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            transform: scale(1.01);
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        /* Enhanced Chat Container */
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 2rem;
            border: 2px solid #e5e7eb;
            border-radius: 20px;
            background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
            margin-bottom: 2rem;
            box-shadow: inset 0 4px 20px rgba(0, 0, 0, 0.05);
        }
        
        .chat-message {
            margin-bottom: 1.5rem;
            padding: 1.2rem 1.8rem;
            border-radius: 24px;
            max-width: 85%;
            position: relative;
            animation: slideIn 0.3s ease;
            font-weight: 500;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-user {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            margin-left: auto;
            text-align: right;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        }
        
        .chat-assistant {
            background: white;
            color: #374151;
            border: 2px solid #e5e7eb;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        /* Enhanced Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 1.2rem 2.5rem !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button:hover::before {
            left: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4) !important;
        }
        
        /* Enhanced Input Fields */
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextInput > div > div > input {
            border: 2px solid #e5e7eb !important;
            border-radius: 16px !important;
            padding: 1.2rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            background: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(10px) !important;
            color: #111827 !important;
            font-weight: 500 !important;
        }
        
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus,
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
            background: white !important;
        }
        
        /* Enhanced Labels */
        .stNumberInput label,
        .stTextInput label,
        .stSelectbox label {
            color: #374151 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            margin-bottom: 0.8rem !important;
        }
        
        /* Loading Spinner */
        .stSpinner > div {
            border-color: #3b82f6 transparent #3b82f6 transparent !important;
        }
        
        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        }
        
        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Success/Error Messages */
        .stAlert {
            border-radius: 16px !important;
            padding: 1.5rem !important;
            font-weight: 500 !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .app-header h1 {
                font-size: 2.5rem;
            }
            
            .app-header p {
                font-size: 1.1rem;
            }
            
            .section-card {
                padding: 1.5rem;
            }
            
            .metric-card {
                padding: 1.5rem;
            }
            
            .metric-value {
                font-size: 2rem;
            }
            
            .section-header {
                font-size: 1.8rem;
            }
            
            .block-container {
                padding: 1rem !important;
            }
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #1d4ed8, #7c3aed);
        }
    </style>
    """