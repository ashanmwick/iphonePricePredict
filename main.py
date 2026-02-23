import streamlit as st
import pandas as pd
import joblib
import numpy as np
import json
from pathlib import Path

st.set_page_config(page_title='📱 Phone Price Predictor', page_icon='📱', layout='wide')

# Load the trained model and feature names
# Load files from the models folder
try:
    base_dir = Path(__file__).resolve().parent
    model_path = base_dir / 'models' / 'random_forest_phone_price_model.pkl'
    feature_names_path = base_dir / 'models' / 'feature_names.json'

    model = joblib.load(model_path)
    with open(feature_names_path, 'r', encoding='utf-8') as f:
        feature_names = json.load(f)
    st.success('✅ Model and feature names loaded successfully!')
except FileNotFoundError:
    st.error('❌ Error: Model or feature names file not found in the models folder.')
    st.stop()

st.title('📱 Phone Price Predictor')
st.caption('✨ Enter phone specifications to predict the estimated market price in LKR.')

condition_features = [f for f in feature_names if f.startswith('Condition_')]
brand_features = [f for f in feature_names if f.startswith('Brand_')]
sim_support_features = [f for f in feature_names if f.startswith('SIM Support_')]
network_features = [f for f in feature_names if f.startswith('Network_')]

condition_options = [f.replace('Condition_', '') for f in condition_features] or ['Used', 'Brand New']
brand_options = [f.replace('Brand_', '') for f in brand_features] or ['Apple', 'Samsung', 'Xiaomi', 'Vivo', 'Google', 'Oppo', 'Huawei', 'Honor', 'Other brand']
sim_support_options = [f.replace('SIM Support_', '') for f in sim_support_features] or ['Dual SIM', 'Single SIM', 'Dual VoLTE']
network_options = [f.replace('Network_', '') for f in network_features] or ['5G', '4G', 'VoLTE']

st.sidebar.title('🧠 Model Details')
st.sidebar.markdown('### 📌 Model Information')
st.sidebar.write('- **Model Type:** Random Forest Regressor')
st.sidebar.write('- **Target:** Phone Price (LKR)')

st.markdown('### 🔧 Enter Phone Specifications')

# Input fields for user
col1, col2 = st.columns(2)

with col1:
    condition = st.selectbox('📦 Condition', condition_options)
    brand = st.selectbox('🏷️ Brand', brand_options)
    ram = st.slider('🧠 RAM (GB)', 1, 16, 4)

with col2:
    memory = st.selectbox('💾 Memory (GB)', [16, 32, 64, 128, 256, 512], index=2)
    sim_support = st.selectbox('📶 SIM Support', sim_support_options)
    network = st.selectbox('🌐 Network', network_options)

if st.button('🚀 Predict Price'):
    # Create a DataFrame from user inputs
    input_data = pd.DataFrame({
        'RAM': [ram],
        'Memory': [memory]
    })

    # Add condition features
    for c in condition_features:
        input_data[c] = 1 if f'Condition_{condition}' == c else 0

    # Add brand features
    for b in brand_features:
        input_data[b] = 1 if f'Brand_{brand}' == b else 0

    # Add SIM Support features
    for s in sim_support_features:
        input_data[s] = 1 if f'SIM Support_{sim_support}' == s else 0

    # Add Network features
    for n in network_features:
        input_data[n] = 1 if f'Network_{network}' == n else 0

    # Ensure all feature_names from training are present, fill missing with 0
    # This handles cases where new categorical values might appear, though unlikely with selectboxes
    for feature in feature_names:
        if feature not in input_data.columns:
            input_data[feature] = 0

    # Reorder columns to match the training data
    input_data = input_data[feature_names]

    # Predict the price
    predicted_price = model.predict(input_data)[0]

    st.success(f'💰 Predicted Phone Price: LKR {predicted_price:,.2f}')