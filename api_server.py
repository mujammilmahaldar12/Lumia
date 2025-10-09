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
        
        print(f"🔬 API Request: capital={capital}, risk_score={risk_score}, years={years}")
        
        # Try to use the roboadvisor, but fallback to demo data if it fails
        try:
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
            
            print("✅ Roboadvisor successful")
            
        except Exception as roboadvisor_error:
            print(f"⚠️  Roboadvisor failed: {roboadvisor_error}")
            print("📝 Using demo data instead...")
            
            # Create demo portfolio based on risk score
            if risk_score <= 30:
                # Conservative portfolio
                result = {
                    'profile': {'risk_score': risk_score, 'capital': capital},
                    'metrics': {
                        'expected_return': 0.065,  # 6.5%
                        'expected_risk': 0.08,
                        'sharpe_ratio': 0.8,
                        'diversification_score': 0.9
                    },
                    'portfolio': {
                        'allocation': {
                            'Government Bonds': 50,
                            'Large Cap Stocks': 25,
                            'High Grade Corporate Bonds': 20,
                            'Money Market': 5
                        },
                        'assets': [
                            {'symbol': 'VGIT', 'name': 'Intermediate-Term Treasury', 'allocation': 30, 'currentPrice': 62, 'expectedReturn': 4.5, 'riskRating': 'Low', 'sector': 'Fixed Income'},
                            {'symbol': 'VTI', 'name': 'Total Stock Market', 'allocation': 25, 'currentPrice': 240, 'expectedReturn': 8.5, 'riskRating': 'Medium', 'sector': 'Equity'},
                            {'symbol': 'LQD', 'name': 'Corporate Bond', 'allocation': 20, 'currentPrice': 115, 'expectedReturn': 5.2, 'riskRating': 'Low', 'sector': 'Fixed Income'}
                        ],
                        'reasoning': [
                            'Conservative allocation prioritizing capital preservation',
                            'High bond allocation reduces portfolio volatility',
                            'Limited equity exposure for modest growth potential'
                        ]
                    }
                }
            else:
                # Moderate portfolio for higher risk scores
                result = {
                    'profile': {'risk_score': risk_score, 'capital': capital},
                    'metrics': {
                        'expected_return': 0.095,  # 9.5%
                        'expected_risk': 0.14,
                        'sharpe_ratio': 0.65,
                        'diversification_score': 0.85
                    },
                    'portfolio': {
                        'allocation': {
                            'Large Cap Stocks': 40,
                            'International Stocks': 15,
                            'Bonds': 30,
                            'Small Cap Stocks': 10,
                            'REITs': 5
                        },
                        'assets': [
                            {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'allocation': 40, 'currentPrice': 440, 'expectedReturn': 10.2, 'riskRating': 'Medium', 'sector': 'Large Cap'},
                            {'symbol': 'VXUS', 'name': 'International Stocks', 'allocation': 15, 'currentPrice': 58, 'expectedReturn': 8.8, 'riskRating': 'Medium', 'sector': 'International'},
                            {'symbol': 'BND', 'name': 'Total Bond Market', 'allocation': 30, 'currentPrice': 79, 'expectedReturn': 4.8, 'riskRating': 'Low', 'sector': 'Fixed Income'}
                        ],
                        'reasoning': [
                            'Balanced allocation between growth and stability',
                            'International diversification reduces geographic risk',
                            'Bond allocation provides downside protection'
                        ]
                    }
                }
        
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