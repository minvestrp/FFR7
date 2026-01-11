"""Entry point — демонстрация загрузки контракта (файл или адрес) и запуска базового анализа."""
import argparse
import logging
import os
import sys
from dotenv import load_dotenv
from modules.analyzer import analyze_contract_from_path
from modules.forensics import TraceAnalyzer

load_dotenv()

logger = logging.getLogger("smartsec")


def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser("SmartSec Audit — main")
    parser.add_argument("--contract", help="Path to Solidity file to analyze")
    parser.add_argument("--address", help="Address to trace (optional)")
    args = parser.parse_args()

    setup_logging()

    if not args.contract and not args.address:
        logger.error("Provide --contract or --address")
        parser.print_help()
        sys.exit(1)

    if args.contract:
        logger.info("Analyzing contract: %s", args.contract)
        contract_arg = args.contract
        # If passed an address, try to fetch source via Etherscan and write to temp file
        if contract_arg.startswith("0x") and len(contract_arg) == 42:
            from modules.extractors.etherscan_fetcher import fetch_contract_source
            import tempfile
            try:
                src = fetch_contract_source(contract_arg)
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=".sol", mode="w", encoding="utf-8")
                tf.write(src)
                tf.flush()
                tf.close()
                contract_path = tf.name
                logger.info("Fetched source to temp file %s", contract_path)
            except Exception as e:
                logger.error("Could not fetch contract source: %s", e)
                print(f"Error fetching contract source: {e}")
                contract_path = None
        else:
            contract_path = contract_arg

        if contract_path:
            res = analyze_contract_from_path(contract_path)
            print("\n=== Contract Analysis ===")
            if res.get("issues"):
                for i, iss in enumerate(res.get("issues"), 1):
                    print(f"{i}. {iss}")
            else:
                print("No issues found (or Slither not available). See raw output for details.")

    if args.address:
        logger.info("Tracing address: %s", args.address)
        ta = TraceAnalyzer()
        for_res = ta.analyze_address(args.address)
        print("\n=== Forensics ===")
        print(for_res.get("summary"))


if __name__ == "__main__":
    main()
