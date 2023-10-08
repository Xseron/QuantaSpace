import json

import joblib
import numpy as np
import os
import openai
import yaml
from flask import (Blueprint, jsonify, redirect, render_template, request,
                   session, url_for)
from gtts import gTTS
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

from .parsersolid import get_beautifull
import PyPDF2

api = Blueprint('api', __name__, template_folder='templates')

# with open('./config.yaml', 'r') as file:
#     cfg = yaml.safe_load(file)
# openai.api_key = cfg["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"]
openai.api_key = "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"

description1 = ""
description2 = "You are an advanced AI bot that analyze the given pdf file, give recomendations, and answer each questions. Be very specific"


def segment_text(text, max_length=500): 
    segments = []
    while text:
        seg = text[:max_length].rsplit('.', 1)[0] + '.'  
        segments.append(seg)
        text = text[len(seg):]
    return segments


def rank_segments(query, segments):
    # print(1)
    # print(query)
    query_words = set(query.lower().split())
    ranked_segments = sorted(segments, key=lambda seg: sum(word in seg.lower() for word in query_words), reverse=True)
    return ranked_segments


def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    with open(pdf_path, "rb") as file:
 
        pdf_reader = PyPDF2.PdfReader(file)
        

        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    
    return text


def count_words(filename):
    with open(filename, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        total_words = 0
        

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            total_words += len(text.split())
            
    return total_words


@api.route("/agro", methods=["GET", "POST"])
def agro():
    if request.method == "POST":

    
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


chat_history2 = [
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
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5, max_tokens = 500)
    chat_history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    write_chat_history(chat_history)
    # page.logger.info(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']



def chat2(question):
    global pdftext
    chat_history2 = read_chat_history2()
    global question_for_analysis
    question_for_analysis = question
    # chat_history.append({"role": "user", "content": question})
    
    # {"role": "assistant", "content": f" {description}"}, 
    # print("asdasdasdasdasd",description)
    # pdftext = 'Space, the vast and mysterious expanse that stretches out infinitely beyond our planet, has captivated the human imagination for centuries. It is a realm of boundless possibilities, where the laws of physics play out on a scale that is almost incomprehensible. From the twinkling stars in the night sky to the distant galaxies that dot the cosmos, space is a canvas upon which the universe paints its masterpiece.'

    messages = [
                {"role": "system", "content": f"chat history: {chat_history2}, {description2}"},
                {"role": "user", "content": f"Based on the text {pdftext}, can you answer in question based on this text:{question}"}
               ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=messages, temperature=0.5, max_tokens = 500)
    chat_history2.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    write_chat_history2(chat_history2)
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
        
        
def read_chat_history2():
    try:
        with open('chat_history2.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    

def write_chat_history2(history):
    with open('chat_history2.json', 'w') as f:
        json.dump(history, f)

@api.route('/pdfupload', methods = ['POST'])   
@api.route('/pdfupload', methods=['POST'])
def success():
    question_for_analysis = 'summorize it'
    if 'file' not in request.files:
        return render_template("error.html", message="No file found.")
    
    f = request.files['file']
    
    if f.filename == '':
        return render_template("error.html", message="No file selected.")
    
    if not allowed_file(f.filename):
        return render_template("error.html", message="Invalid file type.")
    
    secure_file_name = secure_filename(f.filename)
    f.save(secure_file_name)
    
    try:

        total_words = count_words(secure_file_name)
        amount_of_segments = total_words // 500
        reader = extract_text_from_pdf(secure_file_name)

        segments = segment_text(reader)
        # print(question_for_analysis)
        # print(1)
        

        ranked_segments = rank_segments(question_for_analysis, segments)
        print(2)
        global pdftext 
        print(3)
        pdftext = ' '.join(ranked_segments[:amount_of_segments])
        print(f"Segments: {segments}")
        print(f"Question: {question_for_analysis}")

        
    except Exception as e:
        print(e)
        return render_template("error.html", message=str(e))
    
    finally:
        os.remove(secure_file_name)
    
    return render_template("chat2.html")

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    


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
    

@api.route('/chat2', methods=['POST'])
def chat_route2():
    print("chat 2 here")
    question = request.json.get('question')
    
    if question:
        #app.logger.info(f"User question: {question}")  # Log user's question
        # print("Hell world!")
        answer = chat2(question)
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
