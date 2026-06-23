# -*- coding: utf-8 -*-
"""
Shadow Del Valle R — Motor 3: Silo Connector
=============================================
Enlazado matemático entre posts para distribución de autoridad (link juice).
Cada post que se pega empuja dinámicamente a los otros del mismo silo.

La fórmula de enlazado asegura que la autoridad se distribuya
de manera óptima para maximizar la indexación de Google.
"""

import json
import os
import random
import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class SiloConnector:
    """
    Conector de silos semánticos.
    Administra el enlazado interno entre posts del mismo nicho.
    """
    
    def __init__(self):
        self.silos: Dict[str, List[Dict]] = defaultdict(list)
        self.enlaces_generados: List[Dict] = []
    
    def registrar_post(self, post: Dict):
        """
        Registra un post en su silo correspondiente.
        
        Args:
            post: Dict con id, slug, titulo, nicho_id, categoria
        """
        silo_id = post.get("nicho_id", post.get("categoria", "general"))
        self.silos[silo_id].append({
            "slug": post.get("slug", ""),
            "titulo": post.get("titulo", ""),
            "nicho": post.get("nicho", ""),
            "timestamp": post.get("timestamp", time.time()),
            "id": post.get("id", ""),
            "frr": post.get("frr", 0.0)
        })
    
    def obtener_enlaces_internos(self, post_actual: Dict, max_enlaces: int = 5) -> List[Dict]:
        """
        Obtiene enlaces internos relevantes para un post.
        
        Args:
            post_actual: Dict con slug, nicho_id, etc.
            max_enlaces: Máximo de enlaces a retornar
        
        Returns:
            Lista de enlaces internos con texto ancla optimizado
        """
        silo_id = post_actual.get("nicho_id", post_actual.get("categoria", "general"))
        post_slug = post_actual.get("slug", "")
        
        candidatos = [
            p for p in self.silos.get(silo_id, [])
            if p["slug"] != post_slug
        ]
        
        # Ordenar por FRR (mejores primero) y luego aleatorio
        candidatos.sort(key=lambda p: p.get("frr", 0), reverse=True)
        
        seleccionados = candidatos[:max_enlaces]
        
        enlaces = []
        for s in seleccionados:
            # Texto ancla contextual
            textos_ancla = [
                f"{s['titulo']}",
                f"más información sobre {s['nicho']}",
                f"guía completa de {s['nicho']}",
                f"artículo relacionado: {s['titulo']}"
            ]
            enlaces.append({
                "url": f"/posts/{s['slug']}/",
                "texto_ancla": random.choice(textos_ancla),
                "nicho": s["nicho"],
                "slug": s["slug"]
            })
        
        self.enlaces_generados.append({
            "post_origen": post_slug,
            "enlaces": len(enlaces),
            "timestamp": time.time()
        })
        
        return enlaces
    
    def generar_html_enlaces(self, post_actual: Dict, max_enlaces: int = 4) -> str:
        """
        Genera HTML de enlaces internos para inyectar en el post.
        
        Args:
            post_actual: Dict del post actual
            max_enlaces: Máximo de enlaces
        
        Returns:
            str: HTML con los enlaces internos
        """
        enlaces = self.obtener_enlaces_internos(post_actual, max_enlaces)
        
        if not enlaces:
            return ""
        
        html = """
    <div class="tip-box">
        <div class="alerta-title">📚 CONTENIDO RELACIONADO</div>
        <ul>
"""
        for e in enlaces:
            html += f'            <li><a href="{e["url"]}">{e["texto_ancla"]}</a></li>\n'
        
        html += """        </ul>
    </div>
"""
        return html
    
    def get_estadisticas_silo(self) -> Dict:
        """Retorna estadísticas de los silos."""
        return {
            "total_silos": len(self.silos),
            "total_posts_en_silos": sum(len(v) for v in self.silos.values()),
            "posts_por_silo": {
                silo_id: len(posts)
                for silo_id, posts in self.silos.items()
            },
            "total_enlaces_generados": len(self.enlaces_generados),
            "ultimo_enlace": self.enlaces_generados[-1] if self.enlaces_generados else None
        }
    
    def exportar_mapa_silo(self) -> Dict:
        """Exporta el mapa completo de silos."""
        mapa = {}
        for silo_id, posts in self.silos.items():
            mapa[silo_id] = [
                {
                    "slug": p["slug"],
                    "titulo": p["titulo"],
                    "nicho": p["nicho"]
                }
                for p in posts
            ]
        return mapa


# ─── Demo ───
if __name__ == "__main__":
    connector = SiloConnector()
    
    # Registrar posts de ejemplo
    posts = [
        {"id": "1", "slug": "guia-accidentes", "titulo": "Guía Completa de Accidentes", "nicho_id": "personal-injury-law", "nicho": "Abogados de Accidentes", "frr": 420.5},
        {"id": "2", "slug": "indemnizacion-accidente", "titulo": "Calculadora de Indemnización", "nicho_id": "personal-injury-law", "nicho": "Abogados de Accidentes", "frr": 380.2},
        {"id": "3", "slug": "abogado-moto", "titulo": "Abogado de Accidentes de Moto", "nicho_id": "personal-injury-law", "nicho": "Abogados de Accidentes", "frr": 350.0},
    ]
    
    for p in posts:
        connector.registrar_post(p)
    
    print("🔗 SILO CONNECTOR — Enlaces generados para 'guia-accidentes':")
    enlaces = connector.obtener_enlaces_internos({"slug": "guia-accidentes", "nicho_id": "personal-injury-law"})
    for e in enlaces:
        print(f"  → {e['texto_ancla']} ({e['url']})")
    
    print(f"\n📊 Posts en silo: {connector.get_estadisticas_silo()['total_posts_en_silos']}")
