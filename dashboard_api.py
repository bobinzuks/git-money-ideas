#!/usr/bin/env python3
"""
API server for Hidden Gem Discovery Dashboard
Serves live data from continuous_discovery.db
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

DB_PATH = "continuous_discovery.db"

@app.route('/api/gems')
def get_gems():
    """Get all discovered gems"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, stars, forks, category, agentdb_multiplier, url, discovered_at
        FROM discovered_gems
        ORDER BY agentdb_multiplier DESC
        LIMIT 1000
    """)

    gems = []
    for row in cursor.fetchall():
        gems.append({
            'name': row[0],
            'stars': row[1],
            'forks': row[2],
            'category': row[3],
            'agentdb_multiplier': row[4],
            'url': row[5],
            'discovered_at': row[6]
        })

    conn.close()
    return jsonify({'gems': gems})

@app.route('/api/ideas')
def get_ideas():
    """Get AI-generated ideas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, category, agentdb_multiplier, novelty_score, generated_at
        FROM generated_ideas
        ORDER BY agentdb_multiplier DESC
        LIMIT 100
    """)

    ideas = []
    for row in cursor.fetchall():
        ideas.append({
            'name': row[0],
            'category': row[1],
            'agentdb_multiplier': row[2],
            'novelty_score': row[3],
            'generated_at': row[4]
        })

    conn.close()
    return jsonify({'ideas': ideas})

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), AVG(agentdb_multiplier) FROM discovered_gems")
    total_gems, avg_multiplier = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM generated_ideas")
    total_ideas = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        'total_gems': total_gems or 0,
        'avg_multiplier': round(avg_multiplier, 1) if avg_multiplier else 0,
        'total_ideas': total_ideas or 0,
        'total_value': (total_gems or 0) * 50  # $50K per gem estimate
    })

if __name__ == '__main__':
    print("🚀 Starting Discovery Dashboard API on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
