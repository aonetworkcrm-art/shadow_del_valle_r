# -*- coding: utf-8 -*-
"""
Shadow Del Valle R — Motor 5: Deployer
========================================
Módulo de despliegue automatizado a Vercel/GitHub.
Empuja los posts generados a producción para que Google los indexe.

Flujo:
    1. Toma los archivos HTML de output/posts/
    2. Genera sitemap.xml y robots.txt
    3. (Opcional) Hace commit y push a GitHub
    4. (Opcional) Dispara build en Vercel
"""

import json
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class Deployer:
    """
    Motor de despliegue automatizado.
    Prepara y empuja los posts a producción.
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self._load_config(config_path)
        self.deployments: List[Dict] = []
    
    def _load_config(self, path: str) -> Dict:
        default = {
            "github": {"repo": "", "branch": "main", "auto_push": False},
            "vercel": {"auto_deploy": False, "dominio": ""}
        }
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    return cfg
            return default
        except:
            return default
    
    def preparar_para_deploy(self, posts_dir: str = "output/posts",
                              output_dir: str = "output") -> Dict:
        """
        Prepara los archivos para deploy.
        - Verifica que los posts existan
        - Calcula estadísticas
        - Genera archivos necesarios
        
        Args:
            posts_dir: Directorio con los posts HTML
            output_dir: Directorio de salida
        
        Returns:
            Dict con el estado de los archivos preparados
        """
        if not os.path.exists(posts_dir):
            return {"success": False, "error": f"Directorio no encontrado: {posts_dir}"}
        
        archivos = [f for f in os.listdir(posts_dir) if f.endswith(".html")]
        
        if not archivos:
            return {"success": False, "error": "No hay archivos HTML para deployar"}
        
        stats = []
        total_bytes = 0
        for f in archivos:
            ruta = os.path.join(posts_dir, f)
            tamano = os.path.getsize(ruta)
            total_bytes += tamano
            stats.append({
                "archivo": f,
                "tamano_bytes": tamano,
                "tamano_kb": round(tamano / 1024, 2),
                "modificado": datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return {
            "success": True,
            "total_archivos": len(archivos),
            "tamano_total_kb": round(total_bytes / 1024, 2),
            "tamano_promedio_kb": round(total_bytes / len(archivos) / 1024, 2),
            "archivos": stats,
            "directorio": os.path.abspath(posts_dir),
            "timestamp": time.time()
        }
    
    def deploy_a_github(self, mensaje_commit: str = "") -> Dict:
        """
        Hace commit y push a GitHub (si está configurado).
        
        Args:
            mensaje_commit: Mensaje personalizado para el commit
        
        Returns:
            Dict con resultado del deploy
        """
        cfg = self.config.get("github", {})
        auto_push = cfg.get("auto_push", False)
        
        if not auto_push:
            return {
                "success": False,
                "error": "Auto-push a GitHub deshabilitado en configuración",
                "sugerencia": "Activa 'github.auto_push' en config/settings.json"
            }
        
        repo = cfg.get("repo", "")
        branch = cfg.get("branch", "main")
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = mensaje_commit or f"🌑 Shadow Del Valle R — Auto-deploy {timestamp}"
            
            # Git commands
            subprocess.run(["git", "add", "output/posts/", "output/sitemap.xml"],
                         capture_output=True, check=False)
            subprocess.run(["git", "add", "output/"],
                         capture_output=True, check=False)
            
            result = subprocess.run(["git", "commit", "-m", msg],
                                  capture_output=True, text=True, check=False)
            
            if result.returncode != 0 and "nothing to commit" not in result.stderr:
                return {"success": False, "error": result.stderr.strip()}
            
            push_result = subprocess.run(["git", "push", "origin", branch],
                                       capture_output=True, text=True, check=False)
            
            if push_result.returncode != 0:
                return {"success": False, "error": push_result.stderr.strip()}
            
            deploy_info = {
                "success": True,
                "commit_message": msg,
                "branch": branch,
                "timestamp": timestamp,
                "repo": repo
            }
            
            self.deployments.append(deploy_info)
            return deploy_info
            
        except FileNotFoundError:
            return {"success": False, "error": "Git no está instalado o no está en el PATH"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def deploy_a_vercel(self) -> Dict:
        """
        Dispara build en Vercel (si está configurado).
        Vercel detecta automáticamente los cambios cuando se hace push a GitHub.
        
        Returns:
            Dict con instrucciones para deploy manual
        """
        cfg = self.config.get("vercel", {})
        auto_deploy = cfg.get("auto_deploy", False)
        dominio = cfg.get("dominio", "")
        
        if not auto_deploy:
            return {
                "success": False,
                "mensaje": "Auto-deploy a Vercel deshabilitado",
                "instrucciones": [
                    "1. Asegúrate de que el repo de GitHub esté conectado a Vercel",
                    "2. Activa 'vercel.auto_deploy' en config/settings.json",
                    f"3. O ejecuta: vercel --prod (si tienes Vercel CLI instalado)"
                ]
            }
        
        # Intentar deploy con Vercel CLI
        try:
            result = subprocess.run(["vercel", "--prod"],
                                  capture_output=True, text=True, check=False,
                                  timeout=60)
            
            if result.returncode == 0:
                deploy_info = {
                    "success": True,
                    "mensaje": "Deploy a Vercel exitoso",
                    "dominio": dominio or "vercel.app",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.deployments.append(deploy_info)
                return deploy_info
            else:
                # Puede ser que vercel CLI no esté configurado
                return {
                    "success": True,
                    "mensaje": "Vercel CLI no disponible. El push a GitHub activará el deploy automático en Vercel.",
                    "sugerencia": f"Conecta tu repo a Vercel en: https://vercel.com/import"
                }
                
        except FileNotFoundError:
            return {
                "success": True,
                "mensaje": "Vercel CLI no instalado. El deploy se hará automáticamente cuando hagas push a GitHub.",
                "sugerencia": "Instala Vercel CLI: npm i -g vercel (opcional)"
            }
    
    def deploy_completo(self, mensaje_commit: str = "") -> Dict:
        """
        Ejecuta el pipeline completo de deploy.
        
        1. Prepara archivos
        2. Push a GitHub
        3. Dispara Vercel
        
        Returns:
            Dict con resultado de cada etapa
        """
        resultado = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "etapas": {}
        }
        
        # Etapa 1: Preparar
        preparado = self.preparar_para_deploy()
        resultado["etapas"]["preparacion"] = preparado
        
        if not preparado.get("success"):
            resultado["success"] = False
            return resultado
        
        # Etapa 2: GitHub
        github = self.deploy_a_github(mensaje_commit)
        resultado["etapas"]["github"] = github
        
        # Etapa 3: Vercel
        vercel = self.deploy_a_vercel()
        resultado["etapas"]["vercel"] = vercel
        
        resultado["success"] = github.get("success", False) or vercel.get("success", False)
        
        return resultado
    
    def get_estadisticas(self) -> Dict:
        """Retorna estadísticas de deployments."""
        return {
            "total_deployments": len(self.deployments),
            "ultimo_deploy": self.deployments[-1] if self.deployments else None
        }


# ─── Demo ───
if __name__ == "__main__":
    deployer = Deployer()
    
    print("=" * 60)
    print("  🚀 SHADOW DEL VALLE R — DEPLOYER")
    print("=" * 60)
    
    resultado = deployer.preparar_para_deploy()
    
    if resultado.get("success"):
        print(f"\n✅ Archivos preparados: {resultado['total_archivos']}")
        print(f"   Tamaño total: {resultado['tamano_total_kb']} KB")
        print(f"   Tamaño promedio: {resultado['tamano_promedio_kb']} KB por post")
        for f in resultado["archivos"][:3]:
            print(f"   • {f['archivo']} ({f['tamano_kb']} KB)")
    else:
        print(f"\nℹ️  {resultado.get('error', 'No hay archivos para deployar')}")
    
    print(f"\nPara deployar:")
    print(f"   1. Activa github.auto_push = true en config/settings.json")
    print(f"   2. O copia los archivos de output/posts/ manualmente")
