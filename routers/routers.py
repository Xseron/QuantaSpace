from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

page = Blueprint('page', __name__, template_folder='templates')

@page.route('/', methods=['GET'])
def index():
    return render_template('index.html', label="home")

@page.route('/about', methods=['GET'])
def about():
    return render_template('about.html', label="about")

@page.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html', label="contact")

@page.route('/ai', methods=['GET'])
def ai():
    return render_template('chat.html', label="agro")

@page.route('/plants', methods=['GET'])
def plants():
    return render_template('plants.html', label="plants")

@page.route('/agroculture', methods=['GET'])
def agroculture():
    return render_template('agro.html', label="agro")