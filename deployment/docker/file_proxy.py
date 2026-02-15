#!/usr/bin/env python3
"""
Authenticated File Proxy for Team-Specific Challenge Files
Validates CTFd session and serves files based on user's team ID
"""
from flask import Flask, send_file, request, jsonify
import requests
import os
from pathlib import Path

app = Flask(__name__)

# Configuration
CTFD_URL = os.environ.get('CTFD_URL', 'http://ctfd:8000')
CHALLENGES_DIR = Path('/challenges/teams')


def get_team_id_from_session():
    """
    Validate CTFd session and extract team ID
    Returns: (team_id, error_message)
    """
    # Get session cookie from request
    session_cookie = request.cookies.get('session')
    
    if not session_cookie:
        return None, "No session cookie found. Please log in to CTFd first."
    
    try:
        # Validate session with CTFd API
        response = requests.get(
            f'{CTFD_URL}/api/v1/users/me',
            cookies={'session': session_cookie},
            timeout=5
        )
        
        if response.status_code != 200:
            return None, "Invalid or expired session. Please log in again."
        
        user_data = response.json()
        
        # Check if user is in a team
        team_id = user_data.get('data', {}).get('team_id')
        
        if not team_id:
            return None, "You must join a team before downloading challenge files."
        
        return team_id, None
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error validating session with CTFd: {e}")
        return None, "Error communicating with CTFd. Please try again later."
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return None, "An unexpected error occurred."


@app.route('/files/<category>/<filename>')
def download_file(category, filename):
    """
    Download team-specific challenge file
    
    Args:
        category: Challenge category (stego, network, osint, crypto)
        filename: File name to download
    
    Returns:
        File download or error response
    """
    # Validate session and get team ID
    team_id, error = get_team_id_from_session()
    
    if error:
        return jsonify({
            'error': error,
            'authenticated': False
        }), 403
    
    # Construct file path for the user's team
    file_path = CHALLENGES_DIR / f"team{team_id}" / category / filename
    
    # Security check: ensure the file exists and is within the challenges directory
    try:
        file_path = file_path.resolve()
        if not file_path.exists():
            app.logger.warning(f"File not found: {file_path}")
            return jsonify({
                'error': f'File not found: {category}/{filename}',
                'team_id': team_id
            }), 404
        
        # Ensure the file is within the challenges directory (prevent directory traversal)
        if not str(file_path).startswith(str(CHALLENGES_DIR.resolve())):
            app.logger.error(f"Directory traversal attempt: {file_path}")
            return jsonify({'error': 'Invalid file path'}), 403
        
        # Serve the file
        app.logger.info(f"Serving {file_path} to Team {team_id}")
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"Error serving file: {e}")
        return jsonify({'error': 'Error serving file'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ctfd_url': CTFD_URL,
        'challenges_dir': str(CHALLENGES_DIR)
    })


@app.route('/')
def index():
    """Info endpoint"""
    return jsonify({
        'service': 'CTF Team File Proxy',
        'description': 'Authenticated file server for team-specific challenge files',
        'usage': 'GET /files/<category>/<filename> (requires CTFd session)',
        'categories': ['stego', 'network', 'osint', 'crypto'],
        'note': 'You must be logged in to CTFd and assigned to a team'
    })


if __name__ == '__main__':
    # Verify challenges directory exists
    if not CHALLENGES_DIR.exists():
        print(f"WARNING: Challenges directory not found: {CHALLENGES_DIR}")
        print("Make sure to mount the challenges volume correctly")
    
    app.run(host='0.0.0.0', port=8082, debug=False)
