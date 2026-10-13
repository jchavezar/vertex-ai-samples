# -*- coding: utf-8 -*-
"""Registry & Dispatcher for all 33 Standalone Custom UI Design Files (`sq_1_1.py` through `sq_m_5.py`).
Every single demo square renders its own 100% unique full-viewport HTML/CSS/JS application."""

from typing import Callable, Dict
from shared.catalog_data import DOMAINS_BY_ID

from shared.standalone_uis.sq_1_1 import render_sq_1_1
from shared.standalone_uis.sq_1_2 import render_sq_1_2
from shared.standalone_uis.sq_1_3 import render_sq_1_3
from shared.standalone_uis.sq_1_4 import render_sq_1_4
from shared.standalone_uis.sq_1_5 import render_sq_1_5

from shared.standalone_uis.sq_2_1 import render_sq_2_1
from shared.standalone_uis.sq_2_2 import render_sq_2_2
from shared.standalone_uis.sq_2_3 import render_sq_2_3
from shared.standalone_uis.sq_2_4 import render_sq_2_4
from shared.standalone_uis.sq_2_5 import render_sq_2_5

from shared.standalone_uis.sq_3_1 import render_sq_3_1
from shared.standalone_uis.sq_3_2 import render_sq_3_2
from shared.standalone_uis.sq_3_3 import render_sq_3_3
from shared.standalone_uis.sq_3_4 import render_sq_3_4
from shared.standalone_uis.sq_3_5 import render_sq_3_5

from shared.standalone_uis.sq_4_1 import render_sq_4_1
from shared.standalone_uis.sq_4_2 import render_sq_4_2
from shared.standalone_uis.sq_4_3 import render_sq_4_3
from shared.standalone_uis.sq_4_4 import render_sq_4_4
from shared.standalone_uis.sq_4_5 import render_sq_4_5

from shared.standalone_uis.sq_5_1 import render_sq_5_1
from shared.standalone_uis.sq_5_2 import render_sq_5_2
from shared.standalone_uis.sq_5_3 import render_sq_5_3
from shared.standalone_uis.sq_5_4 import render_sq_5_4
from shared.standalone_uis.sq_5_5 import render_sq_5_5

from shared.standalone_uis.sq_6_1 import render_sq_6_1
from shared.standalone_uis.sq_6_2 import render_sq_6_2
from shared.standalone_uis.sq_6_3 import render_sq_6_3

from shared.standalone_uis.sq_m_1 import render_sq_m_1
from shared.standalone_uis.sq_m_2 import render_sq_m_2
from shared.standalone_uis.sq_m_3 import render_sq_m_3
from shared.standalone_uis.sq_m_4 import render_sq_m_4
from shared.standalone_uis.sq_m_5 import render_sq_m_5


STANDALONE_UI_RENDERERS: Dict[str, Callable[[str], str]] = {
    "1.1": render_sq_1_1,
    "1.2": render_sq_1_2,
    "1.3": render_sq_1_3,
    "1.4": render_sq_1_4,
    "1.5": render_sq_1_5,
    "2.1": render_sq_2_1,
    "2.2": render_sq_2_2,
    "2.3": render_sq_2_3,
    "2.4": render_sq_2_4,
    "2.5": render_sq_2_5,
    "3.1": render_sq_3_1,
    "3.2": render_sq_3_2,
    "3.3": render_sq_3_3,
    "3.4": render_sq_3_4,
    "3.5": render_sq_3_5,
    "4.1": render_sq_4_1,
    "4.2": render_sq_4_2,
    "4.3": render_sq_4_3,
    "4.4": render_sq_4_4,
    "4.5": render_sq_4_5,
    "5.1": render_sq_5_1,
    "5.2": render_sq_5_2,
    "5.3": render_sq_5_3,
    "5.4": render_sq_5_4,
    "5.5": render_sq_5_5,
    "6.1": render_sq_6_1,
    "6.2": render_sq_6_2,
    "6.3": render_sq_6_3,
    "M.1": render_sq_m_1,
    "M.2": render_sq_m_2,
    "M.3": render_sq_m_3,
    "M.4": render_sq_m_4,
    "M.5": render_sq_m_5,
}


def render_standalone_square_ui(code: str, auth_token: str, dept_id: str = "sales") -> str:
    """Renders the dedicated standalone full-screen application for the requested square code."""
    norm_code = (code or "").strip().upper()
    if norm_code in STANDALONE_UI_RENDERERS:
        return STANDALONE_UI_RENDERERS[norm_code](auth_token)
    dept = DOMAINS_BY_ID.get(dept_id, DOMAINS_BY_ID["sales"])
    first_code = dept["projects"][0]["code"]
    return STANDALONE_UI_RENDERERS[first_code](auth_token)
