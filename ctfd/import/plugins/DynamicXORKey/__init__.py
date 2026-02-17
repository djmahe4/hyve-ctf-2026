from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.flags import FLAG_CLASSES, BaseFlag
from CTFd.models import db, Challenges, Solves, Flags
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
        Expects provided format: HYVE_CTF{content}
        saved: The base flag content (without the format wrapper)
        """
        # 1. Regex to extract content from provided string
        # Provided: HYVE_CTF{CONTENT}
        match_provided = re.match(r"HYVE_CTF\{(.+)\}", provided)
        if not match_provided:
            return False
        
        provided_content = match_provided.group(1)
        
        # 2. Extract content from saved flag (which might be just content or wrapped)
        match_saved = re.match(r"HYVE_CTF\{(.+)\}", saved)
        if match_saved:
            saved_content = match_saved.group(1)
        else:
            saved_content = saved

        # 3. Check if content matches base flag
        return provided_content == saved_content

def load(app):
    FLAG_CLASSES["dynamic_xor"] = DynamicXORKey
    register_plugin_assets_directory(app, base_path="/plugins/DynamicXORKey/assets/")
