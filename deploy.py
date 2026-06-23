#!/usr/bin/env python3
"""
🚀 Shadow Del Valle R — Deploy Automatizado
=============================================
Script que prepara y empuja los posts generados a producción.

Uso:
    python deploy.py              # Prepara archivos para deploy
    python deploy.py --github     # Hace push a GitHub
    python deploy.py --vercel     # Dispara build en Vercel
    python deploy.py --all        # Pipeline completo
    python deploy.py --status     # Ver estado de los archivos
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.deployer import Deployer


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    DIM = "\033[2m"

def c(text, color, bold=False):
    prefix = Colors.BOLD if bold else ""
    return prefix + color + str(text) + Colors.RESET


def show_header():
    print(f"\n{c('=' * 56, Colors.CYAN, bold=True)}")
    print(c("  🚀 SHADOW DEL VALLE R — DEPLOY AUTOMATIZADO", Colors.CYAN, bold=True))
    print(c(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", Colors.DIM))
    print(c("=" * 56, Colors.CYAN, bold=True))


def cmd_status():
    """Muestra el estado de los archivos listos para deploy."""
    show_header()
    
    deployer = Deployer()
    resultado = deployer.preparar_para_deploy()
    
    if resultado.get("success"):
        print(f"\n{c('✅ Archivos listos para deploy:', Colors.GREEN, bold=True)}")
        print(f"  {c('Total:', Colors.YELLOW)} {resultado['total_archivos']} posts")
        print(f"  {c('Tamaño total:', Colors.YELLOW)} {resultado['tamano_total_kb']} KB")
        print(f"  {c('Tamaño promedio:', Colors.YELLOW)} {resultado['tamano_promedio_kb']} KB por post")
        print(f"\n{c('Archivos:', Colors.CYAN)}")
        for f in resultado["archivos"]:
            print(f"  • {c(f['archivo'], Colors.GREEN)} ({f['tamano_kb']} KB) — {f['modificado']}")
    else:
        print(f"\n{c(resultado.get('error', 'No hay archivos en output/posts/'), Colors.YELLOW)}")
        print(f"\n  {c('Genera algunos posts primero:', Colors.DIM)}")
        print(f"  python shadow_del_valle_r.py    → Menú → Generar Post")
        print(f"  python main_agent.py --once     → Genera un post automático")


def cmd_github():
    """Hace push a GitHub."""
    show_header()
    print(f"\n{c('📤 Empujando a GitHub...', Colors.YELLOW)}")
    
    deployer = Deployer()
    resultado = deployer.deploy_a_github()
    
    if resultado.get("success"):
        print(f"\n{c('✅ Push exitoso:', Colors.GREEN, bold=True)}")
        print(f"  Commit: {resultado['commit_message']}")
        print(f"  Branch: {resultado['branch']}")
        print(f"\n{c('Vercel detectará los cambios automáticamente.', Colors.DIM)}")
    else:
        print(f"\n{c(f'❌ Error: {resultado.get(\"error\", \"Desconocido\")}', Colors.RED)}")
        print(f"\n{c(f'💡 Sugerencia: {resultado.get(\"sugerencia\", \"\")}', Colors.YELLOW)}")
        print(f"\n  {c('O hazlo manualmente:', Colors.DIM)}")
        print("  git add output/")
        print("  git commit -m \"🌑 Shadow Del Valle R - Auto-deploy\"")
        print("  git push")


def cmd_vercel():
    """Dispara build en Vercel."""
    show_header()
    print(f"\n{c('▲ Desplegando a Vercel...', Colors.YELLOW)}")
    
    deployer = Deployer()
    resultado = deployer.deploy_a_vercel()
    
    print(f"\n{c(resultado.get('mensaje', ''), Colors.GREEN)}")
    if resultado.get("sugerencia"):
        print(f"\n{c(f'💡 {resultado[\"sugerencia\"]}', Colors.YELLOW)}")
    if resultado.get("instrucciones"):
        print(f"\n{c('Instrucciones:', Colors.CYAN)}")
        for i in resultado["instrucciones"]:
            print(f"  {i}")


def cmd_all():
    """Pipeline completo: GitHub + Vercel."""
    show_header()
    print(f"\n{c('🔄 Pipeline completo de deploy...', Colors.YELLOW, bold=True)}")
    
    deployer = Deployer()
    
    # 1. Preparar
    print(f"\n{c('📋 1. Preparando archivos...', Colors.CYAN)}")
    preparado = deployer.preparar_para_deploy()
    if preparado.get("success"):
        print(f"     {c(f'{preparado[\"total_archivos\"]} archivos listos', Colors.GREEN)}")
    else:
        print(f"     {c(preparado.get('error', 'Error'), Colors.RED)}")
        return
    
    # 2. GitHub
    print(f"\n{c('📤 2. Push a GitHub...', Colors.CYAN)}")
    github = deployer.deploy_a_github()
    if github.get("success"):
        print(f"     {c('✅ Push exitoso', Colors.GREEN)}")
    else:
        print(f"     {c(github.get('error', 'Error en push'), Colors.YELLOW)}")
    
    # 3. Vercel
    print(f"\n{c('▲ 3. Deploy a Vercel...', Colors.CYAN)}")
    vercel = deployer.deploy_a_vercel()
    print(f"     {c(vercel.get('mensaje', ''), Colors.GREEN)}")
    
    print(f"\n{c('=' * 56, Colors.GREEN, bold=True)}")
    print(c("  🚀 Pipeline completado", Colors.GREEN, bold=True))
    print(c("=" * 56, Colors.GREEN, bold=True))


def main():
    parser = argparse.ArgumentParser(
        description="🌑 Shadow Del Valle R — Deploy Automatizado"
    )
    parser.add_argument("--github", action="store_true", help="Push a GitHub")
    parser.add_argument("--vercel", action="store_true", help="Deploy a Vercel")
    parser.add_argument("--all", action="store_true", help="Pipeline completo")
    parser.add_argument("--status", action="store_true", help="Estado de archivos")
    
    args = parser.parse_args()
    
    if args.github:
        cmd_github()
    elif args.vercel:
        cmd_vercel()
    elif args.all:
        cmd_all()
    elif args.status:
        cmd_status()
    else:
        cmd_status()


if __name__ == "__main__":
    main()
