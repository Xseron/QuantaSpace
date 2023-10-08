import json

import joblib
import numpy as np
import openai
import yaml
from flask import (Blueprint, jsonify, redirect, render_template, request,
                   session, url_for)
from gtts import gTTS

from .parsersolid import get_beautifull

api = Blueprint('api', __name__, template_folder='templates')

with open('./config.yaml', 'r') as file:
    cfg = yaml.safe_load(file)
openai.api_key = cfg["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"]

description = ""

chat_history = [
    {"role": "system", "content": "refer to the previous dialogue if needed"},
]

@api.route('/map', methods=['GET', 'POST'])
def map_source():
    return render_template('map.html')

@api.route('/map_source')
def map():
    render_template("map.html")

# Load the model, scaler, and label encoder
model = joblib.load("./data/fertilizer_random_forest_model_updated.pkl")
scaler = joblib.load("./data/scaler_updated.pkl")
label_encoders = joblib.load("./data/label_encoders.pkl")

@api.route("/plants", methods=["GET", "POST"])
def plants():
    if request.method == "POST":
        # Get data from form
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        moisture = float(request.form["moisture"])
        soil_type = float(request.form["soil_type"])
        crop_type = float(request.form["crop_type"])
        nitrogen = float(request.form["nitrogen"])
        potassium = float(request.form["potassium"])
        phosphorous = float(request.form["phosphorous"])

        # Create numpy array of input data and scale it
        input_data = np.array([[temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous]])
        input_data_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction_encoded = model.predict(input_data_scaled)[0]
        
        print("Label Encoder Keys:", label_encoders.keys())
        print("Encoded Prediction:", prediction_encoded)
        
        prediction = label_encoders['Fertilizer Name'].inverse_transform([prediction_encoded])[0]

        session['messages'] = json.dumps({"type":"1", "Fertilizer Name": prediction, "temp":temperature, "humidity":humidity,
                                                                "moisture":moisture, "soil_type":soil_type, "crop_type":crop_type, "nitrogen":nitrogen,
                                                                "potassium":potassium, "phosphorous": phosphorous})
        
        return redirect(url_for('api.chat_r'))
    
    return render_template("plants.html")

# Load the model, scaler, and label encoder
model_agro = joblib.load("./data/random_forest_model.pkl")
scaler_agro = joblib.load("./data/scaler.pkl")

@api.route("/agro", methods=["GET", "POST"])
def agro():
    if request.method == "POST":

        # Get data from form
        size = str(request.form["N"])
        distance = str(request.form["P"])
        goal = str(request.form["K"])
        passagers = str(request.form["temperature"])

        # message = f'Hello, I generate rocket for travelinf in space with {passagers} passagers, '
        # humidity = float(request.form["humidity"])
        # ph = float(request.form["ph"])
        # rainfall = float(request.form["rainfall"])

        # Create numpy array of input data and scale it
        # input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        # input_data_scaled = scaler_agro.transform(input_data)
        
        # Make prediction
        # prediction = model_agro.predict(input_data_scaled)[0]
        session['messages'] = json.dumps({"type":"1", "size": size, "distance":distance, "goal":goal, "passagers":passagers})
        


        return redirect(url_for('api.chat_r'))
    
    return render_template("agro.html")

chat_history = [
    {"role": "system", "content": "refer to the previous dialogue if needed"},
]

def chat(question):
    # page.logger.info(f"Received question: {question}")
    chat_history = read_chat_history()
    chat_history.append({"role": "user", "content": question})
    
    # {"role": "assistant", "content": f" {description}"}, 
    # print("asdasdasdasdasd",description)
     
    messages = [
                {"role": "system", "content": f"chat history: {chat_history}, {description}"},
                {"role": "assistant", "content": f"Description of a team: {description}, chat history with you:{chat_history}"},
                {"role": "user", "content": f"question: {question}"}
               ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5, max_tokens = 150)
    chat_history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    write_chat_history(chat_history)
    # page.logger.info(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']


def read_chat_history():
    try:
        with open('chat_history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_chat_history(history):
    with open('chat_history.json', 'w') as f:
        json.dump(history, f)



@api.route('/chat', methods=['POST'])
def chat_route():
    question = request.json.get('question')
    if question:
        #app.logger.info(f"User question: {question}")  # Log user's question
        answer = chat(question)
        #app.logger.info(f"Bot answer: {answer}")  # Log bot's answer
        return jsonify({"answer": answer})
    else:
        return jsonify({"error": "Missing question parameter"}), 400
    
@api.route('/chat', methods=['GET'])
def chat_r():
    global description
    quession_data = json.loads(session['messages'])
    if quession_data["type"] == "1":
        # fertilizer
        description = """As an expert in rocket building, help me with the next problem. I need to build rocket to travel in space. Your answer must contain 30 words """
        #[Temperature] (Celcius), [Humidity] (relative humidity in %), [Moisture] (relative moisture in %), [Soil Type], [Crop Type], [Nitrogen] (ratio of Nitrogen content in soil), [Potassium] (ratio of Potassium content in soil), [Phosphorus] (ratio of Phosphorous content in soil), [Fertilizer]
        quessio = f"size: {quession_data['size']}, distance:{quession_data['distance']}, goal: {quession_data['goal']}, passagers: {quession_data['passagers']}"
    else:
        description = """As an expert in rocket building, help me with the next problem. I need to build rocket to travel in space. Your answer must contain 30 words """

        # description = """As an expert in farming and agricultural sectors, help me with the next problem. My AI-based project is intended to help farmers determine the right type of crop. Words in square brackets ("[ ]") are input variables by the user. Input data will contain the next parameters in the corresponding order: [Nitrogen] (ratio of Nitrogen content in soil), [Phosphorus] (ratio of Phosphorous content in soil), [Potassium] (ratio of Potassium content in soil), [Temperature] (Celcius), [Humidity] (relative humidity in %), [Ph] (ph value of the soil), [Rainfall] (Rainfall in millimeters), [Crop Type]. The parameter [Crop Type] is derived from our algorithms. Your ONLY task is to explain why this [Crop Type] is OPTIMAL to be grown, according to [Nitrogen], [Phosphorus], [Potassium], [Humidity], [Ph], [Rainfall] parameters. (MAIN FOCUS MUST BE ON THE [Crop Type]). OPTIMAL means that these parameters are suitable for correct growth of the [Crop Type] and, MOST IMPORTANTLY, that this [Crop Type]'s growth process is as low as possible in terms of harmful emissions, (such as Carbon Dioxide, GHG, Methane, etc.), water and energy consumptions. Also explain (provide at least two reasons) how this positive impact on ecology will be taken further NOW AND IN THE FUTURE (For example, Certain crop types can increase the quality of soil, then something else also happens) (DON'T FOCUS ONLY ON QUALITY OF SOIL HERE). Words in the stars here ("* *") are the values you have to generate by yourself. (DON'T PUT STAR SYMBOLS (*) IN YOUR REPLIES). Write each paragraph of your explanation in the next format: "*NUMBER OF PARAGRAPH*)*PARAGRAPH HEADER*: *EXPLANATION*". Your first message MUST only contain the following: "Enter [Nitrogen], [Phosphorus], [Potassium], [Temperature], [Humidity], [Ph], [Rainfall], [Crop Type] parameters", then you must derive these parameters from the user input. If you want to write something like "Remember to apply *something* properly...", don't write it in your answer. When mentioning values always specify their values and types (E.g: Â°C, mm, ratio in soil, etc.). You MUST limit the number of paragraphs in your answer to 5."""
        quessio = f"size: {quession_data['size']}, distance:{quession_data['distance']}, goal: {quession_data['goal']}, passagers: {quession_data['passagers']}"

        # [Phosphorus] (ratio of Phosphorous content in soil), [Potassium] (ratio of Potassium content in soil), [Temperature] (Celcius), [Humidity] (relative humidity in %), [Ph] (ph value of the soil), [Rainfall] (Rainfall in millimeters), [Crop Type]. The parameter [Crop Type] is derived from our algorithms. Your ONLY task is to explain why this [Crop Type] is OPTIMAL to be grown, according to [Nitrogen], [Phosphorus], [Potassium], [Humidity], [Ph], [Rainfall] parameters. (MAIN FOCUS MUST BE ON THE [Crop Type]). OPTIMAL means that these parameters are suitable for correct growth of the [Crop Type] and, MOST IMPORTANTLY, that this [Crop Type]'s growth process is as low as possible in terms of harmful emissions, (such as Carbon Dioxide, GHG, Methane, etc.), water and energy consumptions. Also explain (provide at least two reasons) how this positive impact on ecology will be taken further NOW AND IN THE FUTURE (For example, Certain crop types can increase the quality of soil, then something else also happens) (DON'T FOCUS ONLY ON QUALITY OF SOIL HERE). Words in the stars here ("* *") are the values you have to generate by yourself. (DON'T PUT STAR SYMBOLS (*) IN YOUR REPLIES). Write each paragraph of your explanation in the next format: "*NUMBER OF PARAGRAPH*)*PARAGRAPH HEADER*: *EXPLANATION*". Your first message MUST only contain the following: "Enter [Nitrogen], [Phosphorus], [Potassium], [Temperature], [Humidity], [Ph], [Rainfall], [Crop Type] parameters"
        # quessio = f"Phosphorus: {quession_data['P']}, Potassium: {quession_data['N']}, Temperature:{quession_data['temperature']}, Humidity: {quession_data['humidity']}, Ph:{quession_data['ph']}, Rainfall: {quession_data['rainfall']}, Crop Type: {quession_data['Crop Type']}"

    return render_template("chat.html", quession=quessio)


@api.route('/asd', methods=['POST'])
def map_location():
    lon = request.json.get('lat')
    lat = request.json.get('lng')
    print(lon, lat)
    if lon and lat:
        return jsonify({"answer": get_beautifull(lon, lat)})
    else:
        return jsonify({"error": "Missing question parameter"}), 400

@api.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    text = request.json.get('text')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    tts = gTTS(text=text, lang='en')
    tts.save('speech.mp3')

    return send_file('speech.mp3', mimetype='audio/mpeg')
