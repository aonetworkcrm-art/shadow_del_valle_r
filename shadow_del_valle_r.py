#!/usr/bin/env python3
"""
Shadow Del Valle R — Centro de Mando
Sistema AaaS de Arbitraje de Trafico
Version 1.0.0 — Junio 2026
"""

import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.radar import Radar
from core.silo_builder import Refinery
from core.silo_connector import SiloConnector
from core.freebuff_bridge import FreeBuffBridge
from core.deployer import Deployer
from core.ledger import Ledger


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"

def c(text, color, bold=False):
    prefix = Colors.BOLD if bold else ""
    return prefix + color + str(text) + Colors.RESET

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def press_enter():
    msg = c("[Presiona Enter para continuar]", Colors.DIM)
    input("\n  " + msg + "  ")

radar = Radar()
refinery = Refinery()
connector = SiloConnector()
bridge = FreeBuffBridge()
deployer = Deployer()
ledger = Ledger()


def show_header():
    clear_screen()
    print()
    print(c("=" * 58, Colors.CYAN, bold=True))
    print(c("  SHADOW DEL VALLE R — CENTRO DE MANDO", Colors.CYAN, bold=True))
    print(c('  "Madera refinada que solo existe aqui"', Colors.DIM))
    print(c("-" * 58, Colors.CYAN))
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    print(c("  v1.0.0 · " + fecha, Colors.DIM))
    print()


def menu_option(num, text, desc=""):
    n_str = str(num)
    print("  " + c("[" + n_str + "]", Colors.GREEN, bold=True) + " " + c(text, Colors.CYAN))
    if desc:
        print("       " + c(desc, Colors.DIM))


def show_radar():
    show_header()
    print(c("  RADAR PREDICTIVO — Factor de Rentabilidad Relativa", Colors.YELLOW, bold=True))
    print(c("  " + "=" * 50, Colors.DIM))

    resultados = radar.escanear_todos()

    print("\n  {:<38} {:>7} {:>10} {:>14}".format('Nicho','CPC','FRR','Estado'))
    print(c("  " + "-" * 69, Colors.DIM))

    for r in sorted(resultados, key=lambda x: x.frr, reverse=True):
        estado = c("APTO", Colors.GREEN) if r.apto else c("DESCARTADO", Colors.RED)
        cpc_str = "${:.0f}".format(r.nicho['cpc_avg'])
        frr_color = Colors.GREEN if r.frr >= radar.umbral_minimo else Colors.RED
        print("  {:<36} {:>7} {:>8}  {}".format(
            r.nicho['name'][:36], cpc_str,
            c("{:.2f}".format(r.frr), frr_color, bold=True), estado))

    aptos = sum(1 for r in resultados if r.apto)
    print("\n  " + c("Umbral FRR:", Colors.YELLOW) + " " + str(radar.umbral_minimo))
    print("  " + c("Nichos aptos:", Colors.GREEN) + " {}/{}".format(aptos, len(resultados)))

    proy = radar.proyectar_ingreso_diario(posts_por_dia=4, clicks_por_post=50)
    print("\n  " + c("PROYECCION (50 clicks/post/dia):", Colors.YELLOW, bold=True))
    print("  " + c("Ingreso diario:", Colors.GREEN) + "    ${:>8,.2f}".format(proy['ingreso_diario_promedio']))
    print("  " + c("Ingreso mensual:", Colors.GREEN) + "   ${:>8,.2f}".format(proy['ingreso_mensual']))
    print("  " + c("Ingreso anual:", Colors.GREEN) + "     ${:>8,.2f}".format(proy['ingreso_anual']))
    press_enter()


def show_ledger():
    show_header()
    ledger.mostrar_dashboard()
    print("\n  " + c("Ultimas transacciones:", Colors.YELLOW, bold=True))
    for t in ledger.get_historial_reciente(8):
        emoji_map = {"ingreso": "💰", "gasto": "💳", "post": "📝", "proyeccion": "📈"}
        emoji = emoji_map.get(t["tipo"], "📌")
        tc = Colors.GREEN if t["tipo"] == "ingreso" else (Colors.RED if t["tipo"] == "gasto" else Colors.CYAN)
        monto_val = t['monto']
        monto_str = "${:>8,.2f}".format(monto_val)
        print("  {} {:<42} {}  {}".format(emoji, t['concepto'][:40], c(monto_str, tc), c(t['fecha_simple'], Colors.DIM)))
    press_enter()


def show_generator():
    show_header()
    print(c("  GENERADOR DE POSTS — Forja de Contenido", Colors.YELLOW, bold=True))
    print(c("  " + "=" * 50, Colors.DIM))

    print("\n  " + c("Selecciona un nicho:", Colors.YELLOW))
    from core.radar import NICHOS_DB
    for i, n in enumerate(NICHOS_DB, 1):
        frr = radar.frr_por_nicho(n["id"])
        cpc_avg = n["cpc_avg"]
        cpc_str = "${:.0f}".format(cpc_avg)
        frr_str = "FRR: {:.2f}".format(frr) if frr else ""
        print("  {} {:<35} {} CPC  {}".format(
            c("[" + str(i) + "]", Colors.GREEN),
            n['name'][:35],
            c(cpc_str, Colors.CYAN),
            c(frr_str, Colors.DIM)))

    print("\n  " + c("[A]", Colors.GREEN) + " Generar para TODOS los nichos aptos")
    print("  " + c("[0]", Colors.RED) + " Volver")

    try:
        choice = input("\n  " + c(">", Colors.GREEN) + " Opcion: ").strip().upper()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "0":
        return
    elif choice == "A":
        resultados = radar.escanear_todos()
        aptos = [r.nicho for r in resultados if r.apto]
        for nicho in aptos[:3]:
            from main_agent import ShadowDelValleAgent
            agent = ShadowDelValleAgent()
            agent._generar_post(nicho)
            print()
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(NICHOS_DB):
                from main_agent import ShadowDelValleAgent
                agent = ShadowDelValleAgent()
                agent._generar_post(NICHOS_DB[idx])
        except (ValueError, IndexError):
            print("\n  " + c("Opcion invalida", Colors.RED))
    press_enter()


def show_deploy():
    show_header()
    print(c("  DEPLOY — Publicar a Produccion", Colors.YELLOW, bold=True))
    print(c("  " + "=" * 50, Colors.DIM))

    preparado = deployer.preparar_para_deploy()
    if preparado.get("success"):
        total_archivos = preparado['total_archivos']
        tam_total = preparado['tamano_total_kb']
        print("\n  " + c("Archivos listos para deploy:", Colors.GREEN, bold=True))
        print("  Total: " + c(str(total_archivos), Colors.GREEN) + " posts")
        print("  Tamano total: " + c(str(tam_total) + " KB", Colors.CYAN))
        for f in preparado["archivos"]:
            print("  * " + c(f['archivo'], Colors.CYAN) + " (" + str(f['tamano_kb']) + " KB)")
        print("\n  " + c("Para deployar a produccion:", Colors.YELLOW))
        print("  1. Activa 'github.auto_push = true' en config/settings.json")
        print("  2. O copia los archivos de output/posts/ manualmente")
        print("  3. O usa Vercel CLI: vercel --prod")
    else:
        print("\n  " + c(preparado.get('error', 'No hay archivos'), Colors.YELLOW))
    press_enter()


def show_config():
    show_header()
    print(c("  CONFIGURACION — Control del Sistema", Colors.YELLOW, bold=True))
    print(c("  " + "=" * 50, Colors.DIM))

    config_path = "config/settings.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        config = {}

    scheduler = config.get("scheduler", {})
    radar_cfg = config.get("radar", {})
    monetag = config.get("monetag", {})

    print("\n  " + c("AGENTE:", Colors.YELLOW, bold=True))
    activo = scheduler.get('agente_activo', True)
    status_color = Colors.GREEN if activo else Colors.RED
    status_str = "ACTIVO" if activo else "PAUSADO"
    print("  Estado:        " + c(status_str, status_color))
    print("  Intervalo:     " + str(scheduler.get('intervalo_generacion_horas', 4.0)) + "h")
    print("  Max posts/dia: " + str(scheduler.get('max_posts_por_dia', 6)))
    print("  Estrategia:    " + scheduler.get('estrategia', 'rotating'))

    print("\n  " + c("RADAR:", Colors.YELLOW, bold=True))
    print("  Umbral FRR:    " + str(radar_cfg.get('umbral_frr_minimo', 150.0)))
    cpc_min = radar_cfg.get('cpc_minimo', 80.0)
    print("  CPC minimo:    $" + str(cpc_min))

    print("\n  " + c("MONETAG:", Colors.YELLOW, bold=True))
    m_activo = monetag.get('habilitado', False)
    m_color = Colors.GREEN if m_activo else Colors.RED
    m_str = "ACTIVO" if m_activo else "DESACTIVADO"
    print("  Estado:        " + c(m_str, m_color))
    print("  Site ID:       " + monetag.get('site_id', 'No configurado'))

    print("\n  " + c("Opciones:", Colors.YELLOW))
    print("  Para cambiar la configuracion, edita: config/settings.json")
    print("  O usa el kill switch: python main_agent.py --kill-switch off")
    press_enter()


def show_agent():
    show_header()
    print(c("  AGENTE AUTONOMO — Modo AaaS", Colors.YELLOW, bold=True))
    print(c("  " + "=" * 50, Colors.DIM))

    print("\n  " + c("ADVERTENCIA:", Colors.RED, bold=True) + " El agente correra en segundo plano.")
    print("  Presiona " + c("Ctrl+C", Colors.YELLOW) + " para detenerlo.")

    print("\n  " + c("[1]", Colors.GREEN) + " Iniciar agente (loop infinito)")
    print("  " + c("[2]", Colors.GREEN) + " Ejecutar una ronda")
    print("  " + c("[3]", Colors.GREEN) + " Ver estado del agente")
    print("  " + c("[0]", Colors.RED) + " Volver")

    try:
        choice = input("\n  " + c(">", Colors.GREEN) + " Opcion: ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "1":
        from main_agent import ShadowDelValleAgent
        agent = ShadowDelValleAgent()
        try:
            agent.run()
        except KeyboardInterrupt:
            print("\n\n  " + c("Agente detenido.", Colors.YELLOW))
    elif choice == "2":
        from main_agent import ShadowDelValleAgent
        agent = ShadowDelValleAgent()
        agent.run_once()
        press_enter()
    elif choice == "3":
        from main_agent import ShadowDelValleAgent
        agent = ShadowDelValleAgent()
        agent.show_status()
        press_enter()


def show_about():
    show_header()
    print(c("  ACERCA DE SHADOW DEL VALLE R", Colors.YELLOW, bold=True))
    print(c("  " + "=" * 50, Colors.DIM))

    print("""
  """ + c("Shadow Del Valle R", Colors.CYAN, bold=True) + """ v1.0.0

  """ + c("Arquitecto:", Colors.YELLOW) + """ Romny (El Joker)
  """ + c("IA Asistente:", Colors.YELLOW) + """ Buffy (Codebuff AI)
  """ + c("Nacimiento:", Colors.YELLOW) + """ 23 de Junio 2026, 3:05 AM

  """ + c("Mision:", Colors.YELLOW, bold=True) + """
  Ser el agente autonomo de arbitraje de trafico mas letal
  del mercado. Cazar intencion anticipada, forjar contenido
  que convierta, y generar ingresos 24/7 sin intervencion humana.

  """ + c("Frase Clave:", Colors.DIM) + """
  "Cuando todos dormian, yo construia el futuro."

  """ + c("Motores:", Colors.YELLOW) + """
  Radar      -> FRR, intencion anticipada, deteccion de nichos
  Refinery   -> HTML ultra-ligero, CSS nativo, Monetag
  Silo       -> Enlazado matematico, distribucion de autoridad
  Bridge     -> Copywriting emotivo, prompts estructurados
  Deployer   -> Vercel/GitHub, publicacion automatica
  Ledger     -> Contabilidad de por vida, dashboard en tiempo real
""")
    press_enter()


def main_menu():
    while True:
        show_header()

        resumen = ledger.get_resumen()
        total_hist = resumen['ingresos']['total_historico']
        total_posts = resumen['proyecciones']['total_posts']
        proy_mes = resumen['proyecciones']['ingreso_proyectado_mensual']

        balance = c("Balance:", Colors.YELLOW)
        historico = c("${:,.2f}".format(total_hist), Colors.GREEN, bold=True)
        posts_str = c(str(total_posts), Colors.CYAN)
        proy_str = c("${:,.2f}".format(proy_mes), Colors.GREEN)
        print("  " + balance + " Historico: " + historico + " | Posts: " + posts_str + " | Proy. mes: " + proy_str)
        print()

        print(c("  SELECCIONA UN MODULO:", Colors.YELLOW, bold=True))
        print()
        menu_option(1, "Radar Predictivo", "Escanea nichos, calcula FRR, proyecta ingresos")
        menu_option(2, "Contabilidad por Vida", "Dashboard financiero en tiempo real, ledger")
        menu_option(3, "Generar Post", "Forja contenido SEO para un nicho especifico")
        menu_option(4, "Deploy", "Prepara y publica posts a produccion")
        menu_option(5, "Configuracion", "Ajustes del sistema, kill switch, Monetag")
        menu_option(6, "Agente Autonomo", "Modo AaaS 24/7 - loop infinito de generacion")
        menu_option(7, "Acerca de", "Informacion del sistema")
        print()
        menu_option(0, "Salir", "Cerrar el Centro de Mando")
        print()

        try:
            choice = input("  " + c(">", Colors.GREEN) + " Opcion: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n" + c("Hasta luego, Joker. El sistema sigue corriendo.", Colors.CYAN))
            sys.exit(0)

        if choice == "1":
            show_radar()
        elif choice == "2":
            show_ledger()
        elif choice == "3":
            show_generator()
        elif choice == "4":
            show_deploy()
        elif choice == "5":
            show_config()
        elif choice == "6":
            show_agent()
        elif choice == "7":
            show_about()
        elif choice == "0":
            print("\n" + c("Hasta luego, Joker. El sistema sigue corriendo.", Colors.CYAN, bold=True))
            print(c('  "La madera refinada nunca deja de crecer."', Colors.DIM))
            print()
            break
        else:
            print("\n  " + c("Opcion invalida. Intenta de nuevo.", Colors.RED))
            press_enter()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n" + c("Hasta luego, Joker. El sistema sigue corriendo.", Colors.CYAN))
        sys.exit(0)
