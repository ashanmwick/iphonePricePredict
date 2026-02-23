import streamlit as st
import pandas as pd
import joblib
import numpy as np

st.set_page_config(page_title='📱 Phone Price Predictor', page_icon='📱', layout='wide')

# Load the trained model and feature names
# Make sure these files are in the same directory as your Streamlit app
try:
    model = joblib.load('model/random_forest_model.joblib')
    feature_names = joblib.load('model/feature_names.joblib')
    st.success('✅ Model and feature names loaded successfully!')
except FileNotFoundError:
    st.error('❌ Error: Model or feature names file not found. Please ensure they are in the same directory as the app.')
    st.stop()

st.title('📱 Phone Price Predictor')
st.caption('✨ Enter phone specifications to predict the estimated market price in LKR.')

st.sidebar.title('🧠 Model Details')
st.sidebar.markdown('### 📌 Model Information')
st.sidebar.write('- **Model Type:** Random Forest Regressor')
st.sidebar.write('- **Target:** Phone Price (LKR)')

st.sidebar.markdown('### 📊 Model Performance')
st.sidebar.info('Performance metrics are generated during training. Add your latest R² / MAE / RMSE values here for quick reference.')

st.markdown('### 🔧 Enter Phone Specifications')

# Input fields for user
col1, col2 = st.columns(2)

with col1:
    condition = st.selectbox('📦 Condition', ['Used', 'Brand New'])
    brand = st.selectbox('🏷️ Brand', ['Apple', 'Samsung', 'Xiaomi', 'Vivo', 'Google', 'Oppo', 'Huawei', 'Honor', 'Other brand'])
    ram = st.slider('🧠 RAM (GB)', 1, 16, 4)

with col2:
    memory = st.selectbox('💾 Memory (GB)', [16, 32, 64, 256, 512], index=2)
    sim_support = st.selectbox('📶 SIM Support', ['Dual SIM', 'Single SIM', 'Dual VoLTE'])
    network = st.selectbox('🌐 Network', ['5G', '4G', 'VoLTE'])

if st.button('🚀 Predict Price'):
    # Create a DataFrame from user inputs
    input_data = pd.DataFrame({
        'RAM': [ram],
        'Memory': [memory],
        'Condition_Brand New': [1 if condition == 'Brand New' else 0],
        'Condition_Used': [1 if condition == 'Used' else 0]
    })

    # Add brand features
    for b in ['Brand_Apple', 'Brand_Google', 'Brand_Honor', 'Brand_Huawei', 'Brand_Oppo', 'Brand_Other brand', 'Brand_Samsung', 'Brand_Vivo', 'Brand_Xiaomi']:
        input_data[b] = 1 if f'Brand_{brand}' == b else 0

    # Add SIM Support features
    for s in ['SIM Support_Dual SIM', 'SIM Support_Dual VoLTE', 'SIM Support_Single SIM']:
        input_data[s] = 1 if f'SIM Support_{sim_support}' == s else 0

    # Add Network features
    for n in ['Network_4G', 'Network_5G', 'Network_VoLTE']:
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