"""cli.py — interfaz de línea de comandos del CRM multi-agente.

Uso:
    python -m crm "Texto libre del lead..."
"""
from __future__ import annotations

import argparse
import json
import sys

from .db import init_db
from .engine import CRMPipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="crm",
        description="Multi-Agent CRM Assistant — procesa leads con agentes IA",
    )
    parser.add_argument("raw_input", help="Texto libre del lead")
    parser.add_argument("--source", default="manual", help="Origen del lead")
    parser.add_argument("--json", action="store_true", help="Imprime resultado como JSON")
    args = parser.parse_args(argv)

    init_db()
    pipeline = CRMPipeline()
    result = pipeline.process(args.raw_input, source=args.source)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print("=" * 70)
    print(f"LEAD: {result.lead.name}")
    if result.lead.company:
        print(f"EMPRESA: {result.lead.company}")
    print(f"SCORE: {result.classification.score}/100 · {result.classification.category.upper()} · urgencia {result.classification.urgency}")
    print("=" * 70)
    print("\nRESUMEN:")
    print(result.summary.text)
    print("\nEMAIL:")
    print(f"Asunto: {result.email.subject}")
    print(result.email.body)
    print("\nPROPUESTA:")
    print(f"Título: {result.proposal.title}")
    print(result.proposal.body)
    if result.proposal.price_estimate:
        print(f"Estimación: {result.proposal.price_estimate}")
    print("\nTAREAS DE SEGUIMIENTO:")
    for t in result.tasks:
        print(f"  - {t.description} (en {t.due_in_days} días)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
