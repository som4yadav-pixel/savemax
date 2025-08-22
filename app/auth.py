from __future__ import annotations

import bcrypt
import streamlit as st

from savemax.app.database import create_user, get_user_hash


SESSION_USER_KEY = "savemax_user"


def is_authenticated() -> bool:
	return bool(st.session_state.get(SESSION_USER_KEY))


def logout() -> None:
	st.session_state.pop(SESSION_USER_KEY, None)


def signup(username: str, password: str) -> bool:
	password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
	return create_user(username, password_hash)


def login(username: str, password: str) -> bool:
	saved_hash = get_user_hash(username)
	if not saved_hash:
		return False
	try:
		if bcrypt.checkpw(password.encode("utf-8"), saved_hash):
			st.session_state[SESSION_USER_KEY] = username
			return True
		return False
	except Exception:
		return False 