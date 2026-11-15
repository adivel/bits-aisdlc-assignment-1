"""CLI entrypoint for Freelance Project Expense & Budget Ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Ensure src/ is importable when invoked as a script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ledger import (  # noqa: E402
    LedgerError,
    add_expense,
    archive_project,
    create_project,
    get_summary,
    list_expenses,
)
from storage import LedgerCorruptedError  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Freelance Project Expense & Budget Ledger CLI")
    parser.add_argument("--ledger", default="ledger.json", help="Path to JSON ledger file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # project subcommands
    proj_parser = subparsers.add_parser("project", help="Manage freelance projects")
    proj_sub = proj_parser.add_subparsers(dest="project_cmd", required=True)

    p_create = proj_sub.add_parser("create", help="Create a new project")
    p_create.add_argument("--id", required=True, dest="project_id")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--client", required=True)
    p_create.add_argument("--budget", required=True)

    p_archive = proj_sub.add_parser("archive", help="Archive a project")
    p_archive.add_argument("--id", required=True, dest="project_id")

    # expense subcommands
    exp_parser = subparsers.add_parser("expense", help="Manage project expenses")
    exp_sub = exp_parser.add_subparsers(dest="expense_cmd", required=True)

    e_add = exp_sub.add_parser("add", help="Add an expense to a project")
    e_add.add_argument("--project", required=True, dest="project_id")
    e_add.add_argument("--amount", required=True)
    e_add.add_argument("--category", required=True)
    e_add.add_argument("--desc", required=True, dest="description")
    e_add.add_argument("--date", required=True, dest="date_str")

    e_list = exp_sub.add_parser("list", help="List expenses for a project")
    e_list.add_argument("--project", required=True, dest="project_id")
    e_list.add_argument("--category", default=None)

    # summary subcommand
    s_parser = subparsers.add_parser("summary", help="Show project budget summary")
    s_parser.add_argument("--project", required=True, dest="project_id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ledger_path = Path(args.ledger)

    try:
        if args.command == "project" and args.project_cmd == "create":
            proj = create_project(ledger_path, args.project_id, args.name, args.client, args.budget)
            result = proj.to_dict()
        elif args.command == "project" and args.project_cmd == "archive":
            proj = archive_project(ledger_path, args.project_id)
            result = proj.to_dict()
        elif args.command == "expense" and args.expense_cmd == "add":
            exp = add_expense(
                ledger_path,
                args.project_id,
                args.amount,
                args.category,
                args.description,
                args.date_str,
            )
            result = exp.to_dict()
        elif args.command == "expense" and args.expense_cmd == "list":
            exps = list_expenses(ledger_path, args.project_id, args.category)
            result = [e.to_dict() for e in exps]
        elif args.command == "summary":
            result = get_summary(ledger_path, args.project_id)
        else:
            parser.print_help()
            return 2
    except (LedgerError, LedgerCorruptedError, ValueError) as exc:
        if args.json_output:
            print(json.dumps({"error": str(exc)}), file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
