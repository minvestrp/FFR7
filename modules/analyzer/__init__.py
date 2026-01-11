"""Анализаторы смарт-контрактов: обёртки для Slither, Mythril, Manticore (стабы)."""
from .slither_wrapper import run_slither_on_file, analyze_contract_from_path

__all__ = ["run_slither_on_file", "analyze_contract_from_path"]
