import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_json(filename):
    filepath = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_json(filename, data):
    filepath = os.path.join(DATA_FOLDER, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== AUTH API ====================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    users = load_json('users.json')
    user = next((u for u in users if u['email'].lower() == email and u['password'] == password), None)

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'phone': user.get('phone', ''),
            'location': user.get('location', '')
        }
    })


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    role = data.get('role', 'farmer').strip()
    phone = data.get('phone', '').strip()
    location = data.get('location', '').strip()

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if role not in ['farmer', 'consumer']:
        return jsonify({'error': 'Role must be farmer or consumer'}), 400

    users = load_json('users.json')

    # Check if email already exists
    if any(u['email'].lower() == email for u in users):
        return jsonify({'error': 'An account with this email already exists'}), 409

    new_id = max([u.get('id', 0) for u in users], default=0) + 1
    new_user = {
        'id': new_id,
        'name': name,
        'email': email,
        'password': password,
        'role': role,
        'phone': phone,
        'location': location,
        'created': datetime.now().strftime('%Y-%m-%d')
    }

    users.append(new_user)
    save_json('users.json', users)

    return jsonify({
        'success': True,
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'role': new_user['role'],
            'phone': new_user['phone'],
            'location': new_user['location']
        }
    }), 201


# ==================== MARKETPLACE API ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    products = load_json('products.json')
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip().lower()

    if category and category != 'All':
        products = [p for p in products if p.get('category', '').lower() == category.lower()]

    if search:
        products = [p for p in products if
                    search in p.get('title', '').lower() or
                    search in p.get('description', '').lower() or
                    search in p.get('location', '').lower()]

    return jsonify(products)


@app.route('/api/products', methods=['POST'])
def add_product():
    products = load_json('products.json')

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    price = request.form.get('price', '0')
    unit = request.form.get('unit', 'per unit').strip()
    location = request.form.get('location', '').strip()
    description = request.form.get('description', '').strip()
    seller = request.form.get('seller', '').strip()
    phone = request.form.get('phone', '').strip()
    seller_id = request.form.get('seller_id', '0')

    if not title or not category or not price:
        return jsonify({'error': 'Title, category, and price are required'}), 400

    image_path = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"/uploads/{filename}"

    # Rental fields
    rental_available = request.form.get('rental_available', '') == 'on'
    rental_price = request.form.get('rental_price', '0')
    rental_unit = request.form.get('rental_unit', 'per day').strip()

    new_id = max([p.get('id', 0) for p in products], default=0) + 1
    new_product = {
        'id': new_id,
        'title': title,
        'category': category,
        'price': int(float(price)),
        'unit': unit,
        'location': location,
        'description': description,
        'seller': seller,
        'phone': phone,
        'seller_id': int(seller_id),
        'image': image_path,
        'posted': datetime.now().strftime('%Y-%m-%d'),
        'rating': 0,
        'rating_count': 0,
        'rental_available': rental_available,
        'rental_price': int(float(rental_price)) if rental_available else 0,
        'rental_unit': rental_unit if rental_available else ''
    }

    products.append(new_product)
    save_json('products.json', products)

    return jsonify(new_product), 201


@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    products = load_json('products.json')
    product_index = next((i for i, p in enumerate(products) if p.get('id') == id), -1)

    if product_index == -1:
        return jsonify({'error': 'Product not found'}), 404

    # Note: In a real app, verify seller_id against session/token here
    products.pop(product_index)
    save_json('products.json', products)

    return jsonify({'success': True, 'message': 'Product deleted successfully'})


# ==================== PRODUCT RATING API ====================

@app.route('/api/products/<int:id>/rate', methods=['POST'])
def rate_product(id):
    data = request.get_json()
    new_rating = data.get('rating', 0)
    user_id = data.get('user_id', 0)

    if not new_rating or new_rating < 1 or new_rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    products = load_json('products.json')
    product = next((p for p in products if p.get('id') == id), None)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Calculate new average rating
    current_rating = product.get('rating', 0) or 0
    current_count = product.get('rating_count', 0) or 0
    new_count = current_count + 1
    new_avg = round(((current_rating * current_count) + new_rating) / new_count, 1)

    product['rating'] = new_avg
    product['rating_count'] = new_count
    save_json('products.json', products)

    return jsonify({'success': True, 'rating': new_avg, 'rating_count': new_count})


# ==================== MARKET PRICES API ====================

@app.route('/api/prices', methods=['GET'])
def get_prices():
    prices = load_json('prices.json')
    search = request.args.get('search', '').strip().lower()

    if search:
        prices = [p for p in prices if
                  search in p.get('crop', '').lower() or
                  search in p.get('market', '').lower()]

    return jsonify(prices)


# ==================== DISEASE DETECTION API ====================

DISEASE_DATABASE = [
    {
        "name": "Bacterial Leaf Blight",
        "confidence": 92.5,
        "description": "A serious rice disease caused by Xanthomonas oryzae. Appears as water-soaked lesions that turn yellow to white along leaf veins.",
        "organic_treatments": [
            "Apply neem oil spray (5ml per liter of water) at weekly intervals",
            "Use Pseudomonas fluorescens bio-agent as seed treatment (10g per kg of seed)",
            "Spray Trichoderma viride solution on affected areas",
            "Ensure proper field drainage to reduce humidity",
            "Remove and destroy infected plant debris"
        ],
        "inorganic_treatments": [
            "Apply Streptocycline (streptomycin sulphate) at 500 ppm concentration",
            "Spray Copper oxychloride (Blitox) at 2.5g per liter of water",
            "Use Plantomycin at 1g per liter as foliar spray",
            "Apply Agrimycin-100 at recommended dosage"
        ]
    },
    {
        "name": "Rice Blast",
        "confidence": 88.3,
        "description": "Caused by Magnaporthe oryzae fungus. Characterized by diamond-shaped lesions with gray centers and dark borders on leaves.",
        "organic_treatments": [
            "Apply Trichoderma harzianum as biological control agent",
            "Use neem cake application at 150 kg per hectare",
            "Spray garlic extract solution (100g crushed garlic in 1L water)",
            "Practice crop rotation with non-host crops",
            "Maintain balanced nitrogen fertilization"
        ],
        "inorganic_treatments": [
            "Spray Tricyclazole (Beam) at 0.6g per liter of water",
            "Apply Carbendazim at 1g per liter as preventive spray",
            "Use Isoprothiolane (Fujione) at 1.5ml per liter",
            "Apply Kasugamycin at recommended concentration"
        ]
    },
    {
        "name": "Late Blight of Tomato",
        "confidence": 95.1,
        "description": "Caused by Phytophthora infestans. Dark water-soaked spots appear on leaves and stems, with white fungal growth on the lower leaf surface.",
        "organic_treatments": [
            "Apply Bordeaux mixture (1%) as preventive spray",
            "Spray copper-based organic fungicide",
            "Use compost tea spray for biological suppression",
            "Remove and destroy infected plant parts immediately",
            "Improve air circulation by proper spacing"
        ],
        "inorganic_treatments": [
            "Spray Mancozeb at 2.5g per liter of water",
            "Apply Metalaxyl + Mancozeb (Ridomil Gold) at 2g per liter",
            "Use Cymoxanil + Mancozeb at recommended dosage",
            "Apply Chlorothalonil (Kavach) at 2g per liter"
        ]
    },
    {
        "name": "Powdery Mildew",
        "confidence": 90.7,
        "description": "A common fungal disease appearing as white powdery spots on leaves and stems. Caused by various species of Erysiphaceae family.",
        "organic_treatments": [
            "Spray diluted milk solution (1 part milk to 9 parts water)",
            "Apply sulfur-based organic fungicide",
            "Use baking soda spray (1 tbsp per gallon of water with soap)",
            "Improve air circulation around plants",
            "Apply neem oil at 2ml per liter of water"
        ],
        "inorganic_treatments": [
            "Apply Wettable Sulfur at 3g per liter of water",
            "Spray Karathane (Dinocap) at 1ml per liter",
            "Use Hexaconazole at 2ml per liter of water",
            "Apply Propiconazole (Tilt) at 1ml per liter"
        ]
    },
    {
        "name": "Leaf Curl Virus",
        "confidence": 87.9,
        "description": "A viral disease transmitted by whiteflies, causing upward curling, puckering, and yellowing of leaves. Common in tomatoes and chillies.",
        "organic_treatments": [
            "Spray neem oil (5ml per liter) to control whitefly vectors",
            "Install yellow sticky traps to monitor and reduce whitefly population",
            "Introduce natural predators like ladybugs and lacewings",
            "Remove and destroy infected plants to prevent spread",
            "Use reflective mulches to repel whiteflies"
        ],
        "inorganic_treatments": [
            "Apply Imidacloprid (0.3ml per liter) to control whiteflies",
            "Spray Thiamethoxam (0.2g per liter) as systemic insecticide",
            "Use Acetamiprid at recommended dosage for vector control",
            "Apply Diafenthiuron at 1g per liter of water"
        ]
    },
    {
        "name": "Fusarium Wilt",
        "confidence": 91.2,
        "description": "A soil-borne fungal disease caused by Fusarium oxysporum. Causes yellowing, wilting, and eventual death of plants starting from lower leaves.",
        "organic_treatments": [
            "Apply Trichoderma viride to soil at 2.5 kg per hectare",
            "Use crop rotation with non-susceptible crops for 3-4 years",
            "Apply bio-compost enriched with beneficial microorganisms",
            "Maintain soil pH between 6.5-7.0 with lime application",
            "Solarize soil before planting during summer months"
        ],
        "inorganic_treatments": [
            "Drench soil with Carbendazim at 1g per liter of water",
            "Apply Benomyl as seed treatment at 2g per kg of seed",
            "Use Thiophanate-methyl as soil application",
            "Apply Copper oxychloride at 3g per liter as preventive"
        ]
    }
]


@app.route('/api/detect-disease', methods=['POST'])
def detect_disease():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if not file or not file.filename:
        return jsonify({'error': 'No image selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400

    # Save the uploaded image
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"disease_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Mock disease detection - select a random disease from database
    import random
    disease = random.choice(DISEASE_DATABASE)

    # Add slight randomness to confidence
    confidence = round(disease['confidence'] + random.uniform(-5, 5), 1)
    confidence = max(60.0, min(99.9, confidence))

    result = {
        'success': True,
        'image_url': f"/uploads/{filename}",
        'disease': {
            'name': disease['name'],
            'confidence': confidence,
            'description': disease['description'],
            'organic_treatments': disease['organic_treatments'],
            'inorganic_treatments': disease['inorganic_treatments']
        }
    }

    return jsonify(result)


# ==================== GOVERNMENT SCHEMES API ====================

@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    schemes = load_json('schemes.json')
    search = request.args.get('search', '').strip().lower()

    if search:
        schemes = [s for s in schemes if
                   search in s.get('title', '').lower() or
                   search in s.get('description', '').lower()]

    return jsonify(schemes)


# ==================== RUN ====================

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
