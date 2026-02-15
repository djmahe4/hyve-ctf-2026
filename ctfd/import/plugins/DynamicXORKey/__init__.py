from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.flags import FLAG_CLASSES, BaseFlag
from CTFd.models import db, Challenges, Solves, Keys
from CTFd.utils.user import get_current_team, get_current_user
from CTFd.utils import config as ctfd_config
from flask import request
import re
import time
import hashlib

class DynamicXORKey(BaseFlag):
    id = 10  # Custom ID
    name = "dynamic_xor"

    @staticmethod
    def compare(saved, provided):
        """
        Expects provided format: HYVE_CTF{content_HASH}
        saved: The base flag content (without the format wrapper and hash)
        """
        # 1. Regex to extract content and hash from provided string
        match = re.match(r"HYVE_CTF\{(.+)_([0-9a-f]{8})\}", provided)
        if not match:
            return False
        
        provided_content = match.group(1)
        provided_hash = match.group(2)
        
        # 2. Check if content matches base flag
        if provided_content != saved:
            return False
            
        # 3. Generate expected hash
        team = get_current_team()
        user = get_current_user()
        identifier = str(team.id if team else user.id)
        
        secret = ctfd_config.get_config("secret_flag_key") or "default_secret"
        
        # Simple XOR hashing as requested
        input_str = f"{saved}|{identifier}|{secret}"
        xor_result = 0
        for char in input_str:
            xor_result ^= ord(char)
        
        expected_hash = format(xor_result, '08x')
        
        return provided_hash == expected_hash

class DecayChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "decay"}
    id = db.Column(None, db.ForeignKey("challenges.id"), primary_key=True)
    decay_rate = db.Column(db.Integer, default=2) # Points to lose
    decay_interval = db.Column(db.Integer, default=240) # Seconds (4 mins)

    def __init__(self, *args, **kwargs):
        super(DecayChallenge, self).__init__(**kwargs)

class DecayChallengeValue(BaseChallenge):
    id = "decay"
    name = "decay"
    templates = {
        "create": "/plugins/DynamicXORKey/assets/create.html",
        "update": "/plugins/DynamicXORKey/assets/update.html",
        "modal": "/plugins/DynamicXORKey/assets/modal.html",
    }
    scripts = {
        "create": "/plugins/DynamicXORKey/assets/create.js",
        "update": "/plugins/DynamicXORKey/assets/update.js",
        "modal": "/plugins/DynamicXORKey/assets/modal.js",
    }

    @staticmethod
    def calculate_value(challenge):
        # Linear decay: 2 pts every 4 mins from competition start
        start_time = ctfd_config.get_config("start") # Competition start timestamp
        if not start_time:
            return challenge.value
            
        now = int(time.time())
        elapsed = max(0, now - int(start_time))
        intervals = elapsed // 240 # 4 minutes
        
        decayed_value = challenge.value - (intervals * 2)
        return max(1, decayed_value) # Minimum 1 point

    @staticmethod
    def attempt(challenge, request):
        data = request.form or request.get_json()
        submission = data.get("submission", "").strip()
        
        flags = Keys.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            if DynamicXORKey.compare(flag.content, submission):
                return True, "Correct"
        return False, "Incorrect"

    @staticmethod
    def solve(user, team, challenge, request):
        value = DecayChallengeValue.calculate_value(challenge)
        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=request.remote_addr,
            provided=request.form.get("submission") or request.get_json().get("submission"),
        )
        # In a real CTFd plugin, we might need to handle the score update here 
        # but for this simulation/logic definition, this is the core.
        db.session.add(solve)
        db.session.commit()

def load(app):
    app.db.create_all()
    FLAG_CLASSES["dynamic_xor"] = DynamicXORKey
    CHALLENGE_CLASSES["decay"] = DecayChallengeValue
    register_plugin_assets_directory(app, base_path="/plugins/DynamicXORKey/assets/")
