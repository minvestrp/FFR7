"""Простейший CLI-запуск анализатора"""
import argparse
import logging
from modules.analyzer import analyze_contract_from_path
from modules.forensics import TraceAnalyzer

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="SmartSec Audit CLI")
    parser.add_argument("--contract", help="Path to Solidity file to analyze")
    parser.add_argument("--address", help="Address to trace (forensics)")
    parser.add_argument("--export", choices=["json", "pdf"], help="Export format for forensics (json|pdf)")
    parser.add_argument("--out", help="Output path for export (file)")
    parser.add_argument("--graph-out", help="Export graph image path (png/svg)")
    parser.add_argument("--graph-format", choices=["png", "svg", "pdf"], default="png", help="Graph image format")
    parser.add_argument("--upload-ipfs", action="store_true", help="Upload exported report to IPFS")
    parser.add_argument("--upload-arweave", action="store_true", help="Upload exported report to Arweave (requires config)")
    args = parser.parse_args()

    if args.contract:
        logger.info("Analyzing contract: %s", args.contract)
        res = analyze_contract_from_path(args.contract)
        print("=== Analysis Result ===")
        for i, issue in enumerate(res.get("issues", []), 1):
            print(i, issue)

    if args.address:
        logger.info("Tracing address: %s", args.address)
        ta = TraceAnalyzer()

        # если указан экспорт — сохраняем расследование в БД и делаем экспорт
        if args.export:
            # ленивое создание БД
            from modules.forensics.db import ForensicsDB
            from modules.reports.reporting import export_investigation_json

            db = ForensicsDB()
            db.init_tables()
            inv_id = ta.analyze_and_store(args.address, db)
            print(f"Investigation saved with id {inv_id}")

            if args.export == "json":
                out_path = args.out or f"investigation_{inv_id}.json"
                export_investigation_json(db, inv_id, out_path)
                print(f"Exported investigation to {out_path}")
                # Optionally upload
                if args.upload_ipfs:
                    from modules.storage.ipfs import upload_file_to_ipfs
                    try:
                        r = upload_file_to_ipfs(out_path)
                        print(f"Uploaded to IPFS: {r.get('hash')}")
                    except Exception as e:
                        print(f"IPFS upload failed: {e}")
                if args.upload_arweave:
                    # Prefer direct Arweave uploader; bundlr fallback is implemented in the arweave wrapper
                    from modules.storage.arweave import upload_file_to_arweave
                    try:
                        r = upload_file_to_arweave(out_path)
                        print(f"Uploaded to Arweave: {r.get('tx_id')}")
                    except Exception as e:
                        print(f"Arweave upload failed: {e}")
            elif args.export == "pdf":
                out_path = args.out or f"investigation_{inv_id}.pdf"
                from modules.reports.reporting import export_investigation_pdf
                try:
                    export_investigation_pdf(db, inv_id, out_path)
                    print(f"Exported investigation PDF to {out_path}")
                    if args.upload_ipfs:
                        from modules.storage.ipfs import upload_file_to_ipfs
                        try:
                            r = upload_file_to_ipfs(out_path)
                            print(f"Uploaded to IPFS: {r.get('hash')}")
                        except Exception as e:
                            print(f"IPFS upload failed: {e}")
                except Exception as e:
                    print(f"PDF export failed: {e}")
            else:
                print("No export format selected.")

            # Graph export
            if args.graph_out:
                from modules.reports.reporting import export_graph_from_db
                try:
                    export_graph_from_db(db, inv_id, args.graph_out, fmt=args.graph_format)
                    print(f"Exported graph image to {args.graph_out}")
                except Exception as e:
                    print(f"Graph export failed: {e}")
        else:
            res = ta.analyze_address(args.address)
            print("=== Forensics Summary ===")
            print(res.get("summary"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
