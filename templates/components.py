"""
Shadow Del Valle R — Componentes CSS Nativos
=============================================
Generadores de componentes visuales sin imágenes.
Cajas de alerta, tablas, botones, badges y más.
Todo con CSS nativo para máxima velocidad.
"""

from typing import List, Optional


def alerta_box(titulo: str, contenido: str, tipo: str = "alerta") -> str:
    """
    Genera una caja de alerta visual.
    
    Args:
        titulo: Título de la alerta
        contenido: Contenido HTML
        tipo: "alerta" | "exito" | "consejo"
    
    Returns:
        str: HTML de la caja de alerta
    """
    class_map = {
        "alerta": "alerta-box",
        "exito": "success-box",
        "consejo": "tip-box"
    }
    emoji_map = {
        "alerta": "⚠️",
        "exito": "✅",
        "consejo": "💡"
    }
    cls = class_map.get(tipo, "alerta-box")
    emoji = emoji_map.get(tipo, "📌")
    
    return f"""<div class="{cls}">
    <div class="alerta-title">{emoji} {titulo}:</div>
    <p>{contenido}</p>
</div>"""


def boton_accion(texto: str, url: str = "#", tipo: str = "primario") -> str:
    """
    Genera un botón de acción.
    
    Args:
        texto: Texto del botón
        url: URL de destino
        tipo: "primario" | "secundario"
    
    Returns:
        str: HTML del botón
    """
    cls = "btn-accion" if tipo == "primario" else "btn-secundario"
    return f'<a href="{url}" class="{cls}">{texto}</a>'


def lista_pasos(pasos: List[str], titulo: str = "Pasos a Seguir") -> str:
    """
    Genera una lista numerada de pasos.
    
    Args:
        pasos: Lista de instrucciones
        titulo: Título de la sección
    
    Returns:
        str: HTML de la lista
    """
    items = "\n".join([f"        <li>{paso}</li>" for paso in pasos])
    return f"""<h2>{titulo}</h2>
<ol>
{items}
</ol>"""


def lista_puntos(puntos: List[str], titulo: str = "") -> str:
    """
    Genera una lista con viñetas.
    
    Args:
        puntos: Lista de elementos
        titulo: Título opcional
    
    Returns:
        str: HTML de la lista
    """
    items = "\n".join([f"        <li>{punto}</li>" for punto in puntos])
    header = f"<h2>{titulo}</h2>\n" if titulo else ""
    return f"""{header}<ul>
{items}
</ul>"""


def cta_box(mensaje: str, boton_texto: str, boton_url: str = "#") -> str:
    """
    Genera una caja de Call-to-Action.
    
    Args:
        mensaje: Mensaje de contexto
        boton_texto: Texto del botón
        boton_url: URL del botón
    
    Returns:
        str: HTML de la CTA
    """
    return f"""<div class="cta-box">
    <p>{mensaje}</p>
    <a href="{boton_url}" class="btn-accion">{boton_texto} →</a>
</div>"""


def parrafo_intro(texto: str) -> str:
    """Genera un párrafo introductorio con énfasis."""
    return f"<p><strong>{texto}</strong></p>"


def tabla_comparativa(filas: List[List[str]], headers: List[str]) -> str:
    """
    Genera una tabla comparativa.
    
    Args:
        filas: Lista de filas, cada una con lista de celdas
        headers: Lista de encabezados
    
    Returns:
        str: HTML de la tabla
    """
    header_row = "".join([f"<th>{h}</th>" for h in headers])
    body_rows = ""
    for fila in filas:
        cells = "".join([f"<td>{c}</td>" for c in fila])
        body_rows += f"        <tr>{cells}</tr>\n"
    
    return f"""<style>
    .tabla-comp{{width:100%;border-collapse:collapse;margin:16px 0;font-size:0.95rem}}
    .tabla-comp th{{background:#d32f2f;color:#fff;padding:10px 12px;text-align:left;font-size:0.85rem}}
    .tabla-comp td{{padding:8px 12px;border-bottom:1px solid #e5e7eb}}
    .tabla-comp tr:hover{{background:#fff5f5}}
</style>
<table class="tabla-comp">
    <thead><tr>{header_row}</tr></thead>
    <tbody>
{body_rows}    </tbody>
</table>"""


def seccion_contenido_relacionado(enlaces: List[dict]) -> str:
    """
    Genera sección de contenido relacionado.
    
    Args:
        enlaces: Lista de dicts con 'url' y 'texto'
    
    Returns:
        str: HTML de la sección
    """
    if not enlaces:
        return ""
    
    items = "\n".join([
        f'            <li><a href="{e["url"]}">{e["texto"]}</a></li>'
        for e in enlaces
    ])
    
    return f"""<div class="tip-box">
    <div class="alerta-title">📚 CONTENIDO RELACIONADO</div>
    <ul>
{items}
    </ul>
</div>"""
