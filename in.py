# hospital_insurance.py

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'hospital_insurance.db'

# ----------------------
# Database Setup
# ----------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Table for patients
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            insurance_id TEXT NOT NULL UNIQUE
        )
    ''')
    # Table for claims
    c.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    conn.commit()
    conn.close()

# ----------------------
# Helper Functions
# ----------------------
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# ----------------------
# Routes
# ----------------------

# Add new patient
@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.json
    name = data.get('name')
    insurance_id = data.get('insurance_id')
    try:
        query_db('INSERT INTO patients (name, insurance_id) VALUES (?, ?)', (name, insurance_id))
        return jsonify({'message': 'Patient added successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Insurance ID already exists'}), 400

# Submit a claim
@app.route('/claims', methods=['POST'])
def submit_claim():
    data = request.json
    patient_id = data.get('patient_id')
    amount = data.get('amount')
    # Check if patient exists
    patient = query_db('SELECT * FROM patients WHERE id = ?', (patient_id,), one=True)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    # Insert claim
    query_db('INSERT INTO claims (patient_id, amount) VALUES (?, ?)', (patient_id, amount))
    return jsonify({'message': 'Claim submitted successfully'}), 201

# Get all claims
@app.route('/claims', methods=['GET'])
def get_claims():
    claims = query_db('''
        SELECT c.id, p.name, c.amount, c.status
        FROM claims c
        JOIN patients p ON c.patient_id = p.id
    ''')
    result = []
    for claim in claims:
        result.append({
            'claim_id': claim[0],
            'patient_name': claim[1],
            'amount': claim[2],
            'status': claim[3]
        })
    return jsonify(result)

# Settle a claim
@app.route('/claims/<int:claim_id>/settle', methods=['POST'])
def settle_claim(claim_id):
    claim = query_db('SELECT * FROM claims WHERE id = ?', (claim_id,), one=True)
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    if claim[3] == 'Settled':
        return jsonify({'error': 'Claim already settled'}), 400
    query_db('UPDATE claims SET status = ? WHERE id = ?', ('Settled', claim_id))
    return jsonify({'message': f'Claim {claim_id} has been settled'})

# ----------------------
# Main
# ----------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
