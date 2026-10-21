"""
Supabase client setup.
Reads SUPABASE_URL and SUPABASE_KEY from environment variables (.env file).
Use the SERVICE ROLE key here (not the anon key) since the backend
manages auth and bypasses row-level security intentionally.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase_client = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set in backend/.env "
                "(copy .env.example to .env and fill in your Supabase project values)."
            )
        _supabase_client = create_client(url, key)
    return _supabase_client
