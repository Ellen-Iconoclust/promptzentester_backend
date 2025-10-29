from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import timedelta, datetime
import uuid

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', '484844884848484wdgdugd2dw22wnkjdndb3dhdjud3u345')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

jwt = JWTManager(app)
CORS(app)

# File paths
USERS_FILE = 'users.json'
PROMPTS_FILE = 'prompts.json'

# Default users
default_users = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin'
    },
    'Ellen': {
        'password': generate_password_hash('password123'),
        'role': 'user'
    },
    'Madelyn': {
        'password': generate_password_hash('password123'),
        'role': 'user'
    },
    'CodeRonins': {
        'password': generate_password_hash('password123'),
        'role': 'user'
    }
}

# Initial prompts data
initial_prompts = [
    {
        'id': 'zen-1',
        'username': 'Ellen',
        'created': '2024-01-15T10:30:00Z',
        'image_url': '/uploads/collectible-figurine.jpg',
        'title': '1/7 Scale Commercialized Figurine',
        'tagline': 'Realistic collectible, desk display',
        'text': 'Create a 1/7 scale commercialized figurine of the characters in the picture, in a realistic style, in a real environment. The figurine is placed on a computer desk. The figurine has a round transparent acrylic base, with no text on the base. The content on the computer screen is a 3D modeling process of this figurine. Next to the computer screen is a toy packaging box, designed in a style reminiscent of high-quality collectible figures, printed with original artwork.',
        'model': 'ChatGPT, Gemini',
        'accepted': True,
        'isTrending': True
    },
    {
        'id': 'zen-2',
        'username': 'Madelyn',
        'created': '2024-01-14T14:20:00Z',
        'image_url': '/uploads/stark-portrait.jpg',
        'title': 'Stark Cinematic Portrait',
        'tagline': 'Cinematic Portrait, dark wardrobe',
        'text': 'Create a vertical portrait shot using the exact same face features, characterized by stark cinematic lighting and intense contrast. Captured in a slightly low, upward-facing angle that dramatized the subject\'s jawline and neck, the composition evokes quite dominance and sculptural elegance. The background is a deep, saturated crimson red, creating a bold visual clash with the model\'s luminous skin and dark wardrobe.',
        'model': 'Gemini',
        'accepted': True,
        'isTrending': True
    },
    {
        'id': 'zen-3',
        'username': 'CodeRonins',
        'created': '2024-01-13T09:15:00Z',
        'image_url': '/uploads/gemini-rose.png',
        'title': 'Aesthetic 90s Style portrait',
        'tagline': 'Retro, romantic environment',
        'text': 'Create a retro vintage grainy but bright image of the reference picture but draped in a perfect red wine color Pinteresty aesthetic retro shirt with white pant and holding a rose flower in hands. It must feel like a 90s movie and romanticising windy environment. The boy is standing against a solid wall deep shadows and contrast drama creating a mysterious and artistic atmosphere where the lighting is warm with a golden tones of evoking a sunset or golden hour glow. The background is minimalist and slightly textured the expression on her face is moody, calm yet happy and introspective.',
        'model': 'Gemini',
        'accepted': True,
        'isTrending': True
    }
]

def load_data():
    """Load users and prompts from JSON files or create default ones"""
    # Load or create users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = default_users
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    
    # Load or create prompts
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r') as f:
            prompts = json.load(f)
    else:
        prompts = initial_prompts
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(prompts, f, indent=2)
    
    return users, prompts

def save_prompts(prompts):
    """Save prompts to JSON file"""
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(prompts, f, indent=2)

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load initial data
users, prompts = load_data()

@app.route('/')
def home():
    return jsonify({"message": "PromptZen API is running!", "status": "success"})

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        # Check if username already exists
        if username in users:
            return jsonify({"error": "Username already exists"}), 400
        
        # Validate username (alphanumeric, 3-20 chars)
        if not username.isalnum() or len(username) < 3 or len(username) > 20:
            return jsonify({"error": "Username must be 3-20 alphanumeric characters"}), 400
        
        # Validate password (at least 6 chars)
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Create new user
        users[username] = {
            'password': generate_password_hash(password),
            'role': 'user'
        }
        
        save_users(users)
        
        # Automatically log in the user after registration
        access_token = create_access_token(
            identity={'username': username, 'role': 'user'}
        )
        
        return jsonify({
            "access_token": access_token,
            "username": username,
            "role": 'user',
            "message": "Registration successful"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            access_token = create_access_token(
                identity={'username': username, 'role': user['role']}
            )
            return jsonify({
                "access_token": access_token,
                "username": username,
                "role": user['role'],
                "message": "Login successful"
            })
        
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    try:
        public_only = request.args.get('public', 'true').lower() == 'true'
        
        if public_only:
            accepted_prompts = [p for p in prompts if p.get('accepted', False)]
            return jsonify(accepted_prompts)
        else:
            return jsonify(prompts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/pending', methods=['GET'])
@jwt_required()
def get_pending_prompts():
    """Get all pending prompts (admin only)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        pending_prompts = [p for p in prompts if not p.get('accepted', False)]
        return jsonify(pending_prompts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts', methods=['POST'])
@jwt_required()
def create_prompt():
    try:
        current_user = get_jwt_identity()
        username = current_user['username']
        
        # Check if it's form data or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            model = request.form.get('model')
            text = request.form.get('text')
            image_file = request.files.get('image')
        else:
            data = request.get_json()
            title = data.get('title')
            tagline = data.get('tagline')
            model = data.get('model')
            text = data.get('text')
            image_file = None
        
        if not all([title, tagline, model, text]):
            return jsonify({"error": "All fields are required"}), 400
        
        # Handle image upload
        image_url = None
        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                image_file.save(filepath)
                image_url = f"/uploads/{unique_filename}"
            else:
                return jsonify({"error": "File type not allowed"}), 400
        
        # Create new prompt
        new_prompt = {
            'id': f"prompt-{uuid.uuid4().hex}",
            'username': username,
            'created': datetime.utcnow().isoformat() + 'Z',
            'image_url': image_url,
            'title': title,
            'tagline': tagline,
            'text': text,
            'model': model,
            'accepted': False,
            'isTrending': False
        }
        
        prompts.append(new_prompt)
        save_prompts(prompts)
        
        return jsonify(new_prompt), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.get_json()
        
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)
        if not prompt:
            return jsonify({"error": "Prompt not found"}), 404
        
        # Update fields
        if 'accepted' in data:
            prompt['accepted'] = data['accepted']
        if 'isTrending' in data:
            prompt['isTrending'] = data['isTrending']
        if 'title' in data:
            prompt['title'] = data['title']
        if 'tagline' in data:
            prompt['tagline'] = data['tagline']
        if 'text' in data:
            prompt['text'] = data['text']
        if 'model' in data:
            prompt['model'] = data['model']
        
        save_prompts(prompts)
        return jsonify(prompt)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        global prompts
        prompts = [p for p in prompts if p['id'] != prompt_id]
        save_prompts(prompts)
        
        return jsonify({"message": "Prompt deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        total_prompts = len(prompts)
        accepted_prompts = len([p for p in prompts if p.get('accepted', False)])
        pending_prompts = len([p for p in prompts if not p.get('accepted', False)])
        trending_prompts = len([p for p in prompts if p.get('isTrending', False) and p.get('accepted', False)])
        total_users = len(set(p['username'] for p in prompts))
        
        return jsonify({
            'total_prompts': total_prompts,
            'accepted_prompts': accepted_prompts,
            'pending_prompts': pending_prompts,
            'trending_prompts': trending_prompts,
            'total_users': total_users
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get public website statistics"""
    try:
        accepted_prompts = [p for p in prompts if p.get('accepted', False)]
        unique_users = set(p['username'] for p in accepted_prompts)
        trending_prompts = [p for p in accepted_prompts if p.get('isTrending', False)]
        
        return jsonify({
            'total_prompts': len(accepted_prompts),
            'total_users': len(unique_users),
            'trending_prompts': len(trending_prompts),
            'categories': 12
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/prompts/bulk-action', methods=['POST'])
@jwt_required()
def bulk_action_prompts():
    """Bulk approve/reject prompts (admin only)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.get_json()
        prompt_ids = data.get('prompt_ids', [])
        action = data.get('action')  # 'approve' or 'reject'
        
        if not prompt_ids or action not in ['approve', 'reject']:
            return jsonify({"error": "Invalid request"}), 400
        
        updated_count = 0
        for prompt_id in prompt_ids:
            prompt = next((p for p in prompts if p['id'] == prompt_id), None)
            if prompt:
                if action == 'approve':
                    prompt['accepted'] = True
                    updated_count += 1
                elif action == 'reject':
                    prompts.remove(prompt)
                    updated_count += 1
        
        if updated_count > 0:
            save_prompts(prompts)
        
        return jsonify({
            "message": f"Successfully {action}d {updated_count} prompts",
            "updated_count": updated_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 PromptZen Backend Server Starting...")
    print(f"📍 Server URL: http://0.0.0.0:{port}")
    print("🔑 Admin Login: admin / admin123")
    print("👥 Sample Users: Ellen, Madelyn, CodeRonins / password123")
    print("\n⚡ Server is running...")
    app.run(debug=False, host='0.0.0.0', port=port)
