"""
Flask API Backend for Lumia Robo-Advisor
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from roboadvisor.user_profile import build_user_profile
from roboadvisor.recommender import generate_recommendation

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Lumia API is running'})

@app.route('/api/generate-portfolio', methods=['POST'])
def generate_portfolio():
    try:
        data = request.get_json()
        
        # Extract parameters
        capital = data.get('capital', 100000)
        risk_score = data.get('riskScore', 50)
        years = data.get('years', 5)
        expected_return = data.get('expectedReturn', 12.0) / 100
        
        # Build user profile
        profile = build_user_profile(
            capital=capital,
            risk_score=risk_score,
            years=years,
            expected_return=expected_return
        )
        
        # Generate recommendation
        db = next(get_db())
        result = generate_recommendation(db, profile, optimize=True)
        db.close()
        
        # Format response
        response = {
            'success': True,
            'data': {
                'profile': result['profile'],
                'metrics': result['metrics'],
                'portfolio': result['portfolio'],
                'total_assets': result.get('total_assets', 0)
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    try:
        data = request.get_json()
        question = data.get('question', '')
        portfolio_data = data.get('portfolio', {})
        
        # Simple AI response simulation
        # In production, integrate with your LumiaAI class
        responses = {
            'risk': 'Based on your risk profile, the portfolio is well-diversified across different asset classes.',
            'return': 'The expected return is calculated using Modern Portfolio Theory and historical data.',
            'allocation': 'The allocation is optimized to balance risk and return based on your preferences.',
            'default': 'I can help you understand your portfolio better. Ask me about risk, returns, or allocations.'
        }
        
        # Simple keyword matching
        response = responses['default']
        for key in responses:
            if key in question.lower():
                response = responses[key]
                break
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)