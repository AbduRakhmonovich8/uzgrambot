import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "Users1"


def create_user(
    user_id,
    username=None,
    number=None,
    twoStepVerify=None,
    setle_phones=None,
    isActive=False,
    logs=None,
    full_name=None,
):
    payload = {
        "user_id": user_id,
        "username": username,
        "number": number,
        "twoStepVerify": twoStepVerify,
        "setle_phones": setle_phones,
        "isActive": isActive,
        "logs": logs,
        "full_name": full_name,
    }
    supabase.table(TABLE_NAME).upsert([payload]).execute()


def get_user(user_id):
    try:
        result = (
            supabase.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"get_user xatolik: {e}")
        return None


def get_all_users():
    result = (
        supabase.table(TABLE_NAME)
        .select(
            "user_id, username, number, isActive, full_name,twoStepVerify,setle_phones,logs"
        )
        .execute()
    )
    return result.data


def get_actives():
    result = supabase.table(TABLE_NAME).select("*").eq("isActive", True).execute()
    return result.data


def get_noactives():
    result = supabase.table(TABLE_NAME).select("*").eq("isActive", False).execute()
    return result.data


def activate_user(user_id):
    supabase.table(TABLE_NAME).update({"isActive": True}).eq(
        "user_id", user_id
    ).execute()


def deactivate_user(user_id):
    supabase.table(TABLE_NAME).update({"isActive": False}).eq(
        "user_id", user_id
    ).execute()


def update_user(user_id, **kwargs):
    if not kwargs:
        return
    supabase.table(TABLE_NAME).update(kwargs).eq("user_id", user_id).execute()


def delete_user(user_id):
    supabase.table(TABLE_NAME).delete().eq("user_id", user_id).execute()
