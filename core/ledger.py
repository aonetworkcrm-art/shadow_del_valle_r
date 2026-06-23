# -*- coding: utf-8 -*-
"""
Shadow Del Valle R — Ledger: Contabilidad de Por Vida
======================================================
Sistema de contabilidad en tiempo real que registra cada transacción,
cada post generado, cada clic estimado y cada dólar proyectado.

"Desde aquí hasta el infinito" — un registro inmutable de todo
el valor generado por el sistema, con respaldo automático.

Características:
    - Registro de cada post generado con su CPC y proyección
    - Cálculo de ingresos en tiempo real (hoy, semana, mes, total histórico)
    - Múltiples fuentes de ingreso (SEO, Monetag, MEV, consultoría)
    - Control de gastos operativos
    - Dashboard financiero con colores en consola
    - Respaldo automático cada 6 horas
    - Exportación a JSON para reportes
    - Proyecciones a futuro
"""

import json
import os
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal, getcontext, ROUND_HALF_DOWN

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN


# ─── Colores para dashboard en consola ───
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"


def c(text, color, bold=False):
    prefix = Colors.BOLD if bold else ""
    return prefix + color + str(text) + Colors.RESET


class LedgerEntry:
    """Una entrada en el libro de contabilidad."""
    
    def __init__(self, entry_type: str, concepto: str, monto: float,
                 fuente: str = "", nicho: str = "", metadata: Optional[Dict] = None):
        self.id = f"TXN-{int(time.time() * 1000)}"
        self.tipo = entry_type  # "ingreso", "gasto", "proyeccion", "post"
        self.concepto = concepto
        self.monto = monto
        self.fuente = fuente
        self.nicho = nicho
        self.metadata = metadata or {}
        self.timestamp = time.time()
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_simple = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "concepto": self.concepto,
            "monto": round(self.monto, 2),
            "fuente": self.fuente,
            "nicho": self.nicho,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "fecha": self.fecha,
            "fecha_simple": self.fecha_simple
        }


class Ledger:
    """
    Libro de contabilidad de por vida.
    Registra cada transacción y genera reportes en tiempo real.
    """
    
    def __init__(self, data_dir: str = "output/ledger"):
        self.data_dir = data_dir
        self.entries: List[LedgerEntry] = []
        self._ultimo_respaldo = 0.0
        self._intervalo_respaldo = 6 * 3600  # 6 horas
        
        os.makedirs(data_dir, exist_ok=True)
        self._cargar_desde_disco()
    
    def _get_db_path(self) -> str:
        """Ruta del archivo de base de datos del ledger."""
        return os.path.join(self.data_dir, "ledger_db.json")
    
    def _get_respaldo_path(self, fecha: str = "") -> str:
        """Ruta del archivo de respaldo."""
        if not fecha:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.data_dir, f"ledger_backup_{fecha}.json")
    
    def _cargar_desde_disco(self):
        """Carga el ledger desde el archivo de persistencia."""
        db_path = self._get_db_path()
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for entry_data in data.get("entries", []):
                    entry = LedgerEntry(
                        entry_type=entry_data["tipo"],
                        concepto=entry_data["concepto"],
                        monto=entry_data["monto"],
                        fuente=entry_data.get("fuente", ""),
                        nicho=entry_data.get("nicho", ""),
                        metadata=entry_data.get("metadata", {})
                    )
                    entry.timestamp = entry_data.get("timestamp", time.time())
                    entry.fecha = entry_data.get("fecha", "")
                    entry.fecha_simple = entry_data.get("fecha_simple", "")
                    entry.id = entry_data.get("id", entry.id)
                    self.entries.append(entry)
            except:
                pass
    
    def _guardar_a_disco(self):
        """Guarda el ledger a disco."""
        db_path = self._get_db_path()
        data = {
            "version": "1.0.0",
            "ultima_actualizacion": time.time(),
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_entries": len(self.entries),
            "entries": [e.to_dict() for e in self.entries]
        }
        try:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Respaldo automático
            ahora = time.time()
            if ahora - self._ultimo_respaldo > self._intervalo_respaldo:
                backup_path = self._get_respaldo_path()
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self._ultimo_respaldo = ahora
        except:
            pass
    
    def registrar_ingreso(self, monto: float, concepto: str,
                          fuente: str = "seo", nicho: str = "") -> LedgerEntry:
        """
        Registra un ingreso en el ledger.
        
        Args:
            monto: Cantidad en USD
            concepto: Descripción del ingreso
            fuente: Fuente del ingreso (seo, monetag, mev, consultoria, etc.)
            nicho: Nicho asociado (opcional)
        
        Returns:
            LedgerEntry creado
        """
        entry = LedgerEntry("ingreso", concepto, monto, fuente, nicho)
        self.entries.append(entry)
        self._guardar_a_disco()
        return entry
    
    def registrar_gasto(self, monto: float, concepto: str,
                        categoria: str = "operativo") -> LedgerEntry:
        """
        Registra un gasto en el ledger.
        
        Args:
            monto: Cantidad en USD
            concepto: Descripción del gasto
            categoria: Categoría del gasto
        
        Returns:
            LedgerEntry creado
        """
        entry = LedgerEntry("gasto", concepto, monto, categoria)
        self.entries.append(entry)
        self._guardar_a_disco()
        return entry
    
    def registrar_post(self, titulo: str, nicho: str, cpc: float,
                       clicks_estimados: int = 0) -> LedgerEntry:
        """
        Registra un post generado con su proyección de ingreso.
        
        Args:
            titulo: Título del post
            nicho: Nicho del post
            cpc: CPC del nicho
            clicks_estimados: Clicks estimados por día
        
        Returns:
            LedgerEntry creado
        """
        ingreso_diario = cpc * clicks_estimados
        entry = LedgerEntry("post", f"Post: {titulo}", ingreso_diario,
                          fuente="seo_content", nicho=nicho,
                          metadata={
                              "cpc": cpc,
                              "clicks_estimados_diarios": clicks_estimados,
                              "ingreso_diario_proyectado": ingreso_diario
                          })
        self.entries.append(entry)
        self._guardar_a_disco()
        return entry
    
    def registrar_proyeccion(self, monto: float, descripcion: str,
                             periodo: str = "mensual") -> LedgerEntry:
        """Registra una proyección de ingreso futuro."""
        entry = LedgerEntry("proyeccion", descripcion, monto,
                          metadata={"periodo": periodo})
        self.entries.append(entry)
        self._guardar_a_disco()
        return entry
    
    def get_resumen(self) -> Dict:
        """
        Genera un resumen financiero completo en tiempo real.
        
        Returns:
            Dict con todas las métricas financieras
        """
        ahora = time.time()
        hoy = datetime.now().strftime("%Y-%m-%d")
        inicio_semana = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        inicio_mes = datetime.now().strftime("%Y-%m-01")
        
        total_ingresos = 0.0
        total_gastos = 0.0
        total_proyecciones = 0.0
        total_posts = 0
        
        ingresos_hoy = 0.0
        ingresos_semana = 0.0
        ingresos_mes = 0.0
        
        posts_por_nicho = defaultdict(int)
        ingresos_por_fuente = defaultdict(float)
        
        for entry in self.entries:
            fecha = entry.fecha_simple
            monto = entry.monto
            
            if entry.tipo == "ingreso":
                total_ingresos += monto
                ingresos_por_fuente[entry.fuente] += monto
                
                if fecha == hoy:
                    ingresos_hoy += monto
                if fecha >= inicio_semana:
                    ingresos_semana += monto
                if fecha >= inicio_mes:
                    ingresos_mes += monto
                    
            elif entry.tipo == "gasto":
                total_gastos += monto
                
            elif entry.tipo == "post":
                total_posts += 1
                if entry.nicho:
                    posts_por_nicho[entry.nicho] += 1
                # Los posts también cuentan como ingresos proyectados
                total_proyecciones += monto
                
            elif entry.tipo == "proyeccion":
                total_proyecciones += monto
        
        return {
            "timestamp": ahora,
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ingresos": {
                "hoy": round(ingresos_hoy, 2),
                "esta_semana": round(ingresos_semana, 2),
                "este_mes": round(ingresos_mes, 2),
                "total_historico": round(total_ingresos, 2)
            },
            "gastos": {
                "total": round(total_gastos, 2)
            },
            "profit_neto": round(total_ingresos - total_gastos, 2),
            "proyecciones": {
                "total_posts": total_posts,
                "ingreso_proyectado_total": round(total_proyecciones, 2),
                "ingreso_proyectado_mensual": round(total_proyecciones, 2) if total_posts > 0 else 0,
                "ingreso_proyectado_anual": round(total_proyecciones * 12, 2) if total_posts > 0 else 0
            },
            "posts_por_nicho": dict(posts_por_nicho),
            "ingresos_por_fuente": {k: round(v, 2) for k, v in ingresos_por_fuente.items()},
            "total_transacciones": len(self.entries),
            "total_posts_generados": total_posts
        }
    
    def get_historial_reciente(self, count: int = 10) -> List[Dict]:
        """Retorna las últimas entradas del ledger."""
        recent = sorted(self.entries, key=lambda e: e.timestamp, reverse=True)
        return [e.to_dict() for e in recent[:count]]
    
    def mostrar_dashboard(self):
        """Muestra el dashboard financiero en consola con colores."""
        r = self.get_resumen()
        
        print("\n" + c("=" * 60, Colors.CYAN, bold=True))
        print(c("  📊 SHADOW DEL VALLE R — DASHBOARD FINANCIERO", Colors.CYAN, bold=True))
        print(c("=" * 60, Colors.CYAN, bold=True))
        
        total_historico = r['ingresos']['total_historico']
        fecha_gen = r['fecha_generacion']
        total_tx = r['total_transacciones']
        
        print(f"\n{c('💰 INGRESOS', Colors.GREEN, bold=True)}")
        print(f"  {c('Hoy:', Colors.GREEN)}         ${r['ingresos']['hoy']:>8,.2f}")
        print(f"  {c('Esta Semana:', Colors.GREEN)}  ${r['ingresos']['esta_semana']:>8,.2f}")
        print(f"  {c('Este Mes:', Colors.GREEN)}     ${r['ingresos']['este_mes']:>8,.2f}")
        print(f"  {c('Total Histórico:', Colors.GREEN, bold=True)} {c('${:>8,.2f}'.format(total_historico), Colors.GREEN, bold=True)}")
        
        print(f"\n{c('📈 PROYECCIONES', Colors.CYAN, bold=True)}")
        print(f"  {c('Posts generados:', Colors.CYAN)}         {r['proyecciones']['total_posts']}")
        print(f"  {c('Ingreso proyectado/mes:', Colors.CYAN)}  ${r['proyecciones']['ingreso_proyectado_mensual']:>8,.2f}")
        print(f"  {c('Ingreso proyectado/año:', Colors.CYAN)}  ${r['proyecciones']['ingreso_proyectado_anual']:>8,.2f}")
        
        print(f"\n{c('💳 GASTOS', Colors.RED, bold=True)}")
        print(f"  {c('Total:', Colors.RED)}          ${r['gastos']['total']:>8,.2f}")
        
        profit = r['profit_neto']
        profit_color = Colors.GREEN if profit >= 0 else Colors.RED
        print(f"\n{c('💵 PROFIT NETO:', Colors.BOLD)}{c(' ${:>8,.2f}'.format(profit), profit_color, bold=True)}")
        
        if r['posts_por_nicho']:
            print(f"\n{c('📋 POSTS POR NICHO:', Colors.YELLOW, bold=True)}")
            for nicho, count in sorted(r['posts_por_nicho'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {nicho:<35} {c(str(count), Colors.GREEN)} posts")
        
        print(f"\n{c('=' * 60, Colors.CYAN)}")
        print(c('  Ultima actualizacion: ' + fecha_gen, Colors.DIM))
        print(c('  Total transacciones: ' + str(total_tx), Colors.DIM))
        print(c("=" * 60, Colors.CYAN, bold=True))
    
    def exportar_reporte(self, filepath: str = "") -> str:
        """Exporta el ledger completo a un archivo JSON."""
        if not filepath:
            filepath = os.path.join(self.data_dir, f"reporte_ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        data = self.get_resumen()
        data["historial"] = self.get_historial_reciente(50)
        data["todas_transacciones"] = [e.to_dict() for e in self.entries]
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath


# ─── Demo / Uso directo ───
if __name__ == "__main__":
    ledger = Ledger()
    
    # Simular algunas transacciones
    ledger.registrar_ingreso(1250.00, "Pago Monetag - Semana 1", "monetag", "Abogados de Accidentes")
    ledger.registrar_ingreso(850.00, "Pago Monetag - Semana 1", "monetag", "Seguros de Vida")
    ledger.registrar_post("Guía de Accidentes", "Abogados de Accidentes", 220.0, 50)
    ledger.registrar_post("Seguro para Adultos", "Seguros de Vida", 95.0, 30)
    ledger.registrar_proyeccion(5000.00, "Proyección mensual SEO", "mensual")
    ledger.registrar_gasto(50.00, "Vercel Pro Plan", "hosting")
    
    ledger.mostrar_dashboard()
    
    print("\n\n📋 Últimas transacciones:")
    for t in ledger.get_historial_reciente(5):
        emoji = {"ingreso": "💰", "gasto": "💳", "post": "📝", "proyeccion": "📈"}.get(t["tipo"], "📌")
        print(f"  {emoji} {t['concepto'][:40]:<42} ${t['monto']:>8,.2f}  ({t['fecha_simple']})")
