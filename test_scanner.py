import asyncio
from codebase_rag.auto_scanner import AutoScanner

async def test():
    scanner = AutoScanner(host='127.0.0.1', port=7687)
    report = await scanner.run_full_scan("dab484f291144101")
    print(f"Total Findings: {report.summary.total}")
    for f in report.findings:
        print(f" - {f.category}: {f.title} ({len(f.blast_radius)} nodes)")

if __name__ == "__main__":
    asyncio.run(test())
