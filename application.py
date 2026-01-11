import joblib
import pandas as pd
from flask import Flask, request, jsonify, render_template # ДОДАНО render_template
from warnings import simplefilter
from flask_cors import CORS 

simplefilter(action='ignore', category=UserWarning)

# AWS Elastic Beanstalk очікує назву 'application'
application = Flask(__name__)
CORS(application)

MODEL_PATH = 'model_artifacts/svc_best_classifier.pkl'
SCALER_PATH = 'model_artifacts/scaler.pkl'

FEATURE_ORDER = [
    'age', 'trestbps', 'chol', 'fbs', 'thalch', 'exang', 'oldpeak', 'ca', 
    'sex_Male',
    'cp_atypical angina', 'cp_non-anginal', 'cp_typical angina',
    'restecg_normal', 'restecg_st-t abnormality',
    'slope_flat', 'slope_upsloping',
    'thal_normal', 'thal_reversable defect'
]

try:
    loaded_model = joblib.load(MODEL_PATH)
    loaded_scaler = joblib.load(SCALER_PATH)
    print("Model and scaler loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    loaded_model = None
    loaded_scaler = None

# --- НОВИЙ МАРШРУТ ДЛЯ ВІДОБРАЖЕННЯ ВАШОГО САЙТУ ---
@application.route('/')
def index():
    # Ця функція шукає файл templates/index.html
    return render_template('index.html')

def preprocess_input(input_data):
    df = pd.DataFrame(0, index=[0], columns=FEATURE_ORDER)
    
    numerical = ['age', 'trestbps', 'chol', 'fbs', 'thalch', 'exang', 'oldpeak', 'ca']
    for feat in numerical:
        if feat in input_data:
            df[feat] = input_data[feat]
    
    if input_data.get('sex') == 'Male':
        df['sex_Male'] = 1
    
    cp = input_data.get('cp', '')
    if cp == 'atypical angina':
        df['cp_atypical angina'] = 1
    elif cp in ['non-anginal', 'non-anginal pain']:
        df['cp_non-anginal'] = 1
    elif cp == 'typical angina':
        df['cp_typical angina'] = 1
    
    restecg = input_data.get('restecg', '')
    if restecg == 'normal':
        df['restecg_normal'] = 1
    elif restecg == 'st-t abnormality':
        df['restecg_st-t abnormality'] = 1
    
    slope = input_data.get('slope', '')
    if isinstance(slope, (int, float)):
        slope = {1: 'upsloping', 2: 'flat', 3: 'downsloping'}.get(int(slope), '')
    
    if slope == 'flat':
        df['slope_flat'] = 1
    elif slope == 'upsloping':
        df['slope_upsloping'] = 1
    
    thal = input_data.get('thal', '')
    if thal == 'normal':
        df['thal_normal'] = 1
    elif thal == 'reversable defect':
        df['thal_reversable defect'] = 1
    
    return loaded_scaler.transform(df)


@application.route('/predict', methods=['POST'])
def predict():
    if not loaded_model or not loaded_scaler:
        return jsonify({
            'status': 'error',
            'error': 'Model unavailable.'
        }), 500

    try:
        data = request.get_json(force=True)
        input_scaled = preprocess_input(data)
        
        prediction = loaded_model.predict(input_scaled)[0]
        probability = loaded_model.predict_proba(input_scaled)[0, 1]
        
        return jsonify({
            'status': 'success',
            'prediction_class': int(prediction),
            'risk_level': 'ВИСОКИЙ РИЗИК ХВОРОБИ СЕРЦЯ' if prediction == 1 else 'НИЗЬКИЙ РИЗИК ХВОРОБИ СЕРЦЯ',
            'probability_disease': round(probability, 4)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Processing error: {str(e)}'
        }), 500


@application.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': loaded_model is not None,
        'scaler_loaded': loaded_scaler is not None
    })


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=False)
