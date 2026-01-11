"""
Простой обёртка для запуска Slither и парсинга результата.
Если Slither недоступен — используется упрощённый статический анализ (по шаблонам).
"""
import os
import json
import shutil
import subprocess
import tempfile
from typing import Dict, Any

# Простые сигнатуры для быстрых эвристик
SUSPICIOUS_PATTERNS = ["delegatecall", "call.value", "selfdestruct", "tx.origin", "transfer"]


def run_slither_on_file(sol_path: str) -> Dict[str, Any]:
    """Попытаться запустить Slither на файле и вернуть словарь с результатами.

    Возвращает:
        dict: {'success': bool, 'issues': list, 'raw': dict_or_str}
    """
    slither_cmd = os.getenv("SLITHER_PATH", "slither")
    if not shutil.which(slither_cmd):
        return {"success": False, "issues": [], "raw": "slither-not-found"}

    tmp_json = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp_json.close()
    try:
        cmd = [slither_cmd, sol_path, "--json", tmp_json.name]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(tmp_json.name, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Примитивный парсинг — Slither возвращает 'results' с 'detectors'
        issues = []
        detectors = data.get("detectors", []) if isinstance(data, dict) else []
        for d in detectors:
            issues.append({"check": d.get("check"), "description": d.get("description")})
        return {"success": True, "issues": issues, "raw": data}
    except subprocess.CalledProcessError as e:
        return {"success": False, "issues": [], "raw": e.stderr.decode()}
    except Exception as e:  # fallback
        return {"success": False, "issues": [], "raw": str(e)}
    finally:
        try:
            os.unlink(tmp_json.name)
        except Exception:
            pass


def analyze_contract_from_path(sol_path: str) -> Dict[str, Any]:
    """Возвращает базовый список подозрительных мест: сначала Slither, затем эвристики.
    """
    res = run_slither_on_file(sol_path)
    if res.get("success"):
        # если есть результаты, вернуть их
        return res

    # fallback: простая эвристика по тексту
    issues = []
    try:
        with open(sol_path, "r", encoding="utf-8") as f:
            src = f.read()
        for p in SUSPICIOUS_PATTERNS:
            if p in src:
                issues.append({"pattern": p, "message": f"Found pattern '{p}' in source"})
    except Exception as e:
        issues.append({"error": str(e)})

    return {"success": False, "issues": issues, "raw": None}
