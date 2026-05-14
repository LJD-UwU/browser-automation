"""
config.py
=========
Configuración central del proyecto: URLs y credenciales.

Edita este archivo para cambiar las variables de los flujos de automatización.
Las claves aquí definidas se usan como variables ${KEY} en los archivos JSON
de pasos (steps_flows/data/json/*.json).
"""

CONFIG = {
    # ── URLs ──────────────────────────────────────────────────────────────────
    "mailLogin":          "https://mail.hisense.com/",
    "BasePlan":           "https://ovsaps.hisense.com/planManageMent/planQuickPhoto",
    "RealTimeProduction": "https://mom.hisense.com/mom_pc/MESRouter/V9DEflJyVn",
    "plmBusqueda":        "https://plm.hisense.com/3dspace/common/emxNavigator.jsp",

    # ── Credenciales ──────────────────────────────────────────────────────────
    "NAME_KEY":     "danira.miranda",
    "PASSWORD_KEY": "SYn3lCnhx0ljIy",
}
