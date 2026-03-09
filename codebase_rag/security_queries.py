"""Security Query Bank — Pre-defined Cypher queries for vulnerability detection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityQuery:
    id: str
    category: str
    severity: str
    title: str
    cypher: str
    description: str


QUERY_BANK: list[SecurityQuery] = [
    # ── Injection ─────────────────────────────────────────────────────
    SecurityQuery(
        id="sqli_paths",
        category="SQL Injection",
        severity="critical",
        title="Potential SQL Injection Paths",
        cypher=r"""
MATCH (f)
WHERE (f:Function OR f:Class OR f:File) AND f.source_code IS NOT NULL
  AND f.source_code =~ "[\\s\\S]*(execute|raw_sql|cursor)[\\s\\S]*f['\"].*\\{.*\\}[\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Detects function call chains that reach database query/execute "
            "methods using f-strings or unsanitized concatenation."
        ),
    ),
    SecurityQuery(
        id="command_injection",
        category="Command Injection",
        severity="critical",
        title="Potential Command Injection",
        cypher=r"""
MATCH (f)
WHERE (f:Function OR f:Class OR f:File) AND f.source_code IS NOT NULL
  AND f.source_code =~ "[\\s\\S]*(os\\.system|subprocess\\.call|subprocess\\.Popen|exec\\(|eval\\()[\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Finds functions using dangerous system execution calls "
            "like os.system(), subprocess.call(), exec(), or eval()."
        ),
    ),
    # ── Secrets ───────────────────────────────────────────────────────
    SecurityQuery(
        id="hardcoded_secrets",
        category="Hardcoded Secrets",
        severity="critical",
        title="Hardcoded Secrets & API Keys",
        cypher=r"""
MATCH (f)
WHERE (f:Function OR f:Class OR f:File) AND f.source_code IS NOT NULL
  AND toLower(f.source_code) =~ "[\\s\\S]*(password|secret|api_key|access_key|api_secret|token|private_key)\\s*=\\s*['\"][a-z0-9_\\-!@#$%^]{8,}['\"][\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Detects hardcoded passwords, API keys, tokens, and other "
            "secrets assigned as string literals."
        ),
    ),
    # ── Crypto ────────────────────────────────────────────────────────
    SecurityQuery(
        id="insecure_crypto",
        category="Insecure Cryptography",
        severity="high",
        title="Weak Cryptographic Algorithms",
        cypher=r"""
MATCH (f)
WHERE (f:Function OR f:Class OR f:File) AND f.source_code IS NOT NULL
  AND toLower(f.source_code) =~ "[\\s\\S]*(md5|sha1|des|rc4|ecb|blowfish)[\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Finds usage of deprecated or weak cryptographic algorithms "
            "such as MD5, SHA1, DES, RC4, or ECB mode."
        ),
    ),
    # ── Access Control ────────────────────────────────────────────────
    SecurityQuery(
        id="missing_auth",
        category="Missing Authentication",
        severity="high",
        title="Endpoints Without Authentication Decorators",
        cypher=r"""
MATCH (f:Function)
WHERE f.decorators IS NOT NULL
  AND ANY(d IN f.decorators WHERE toLower(d) =~ "[\\s\\S]*(route|get|post|put|delete|patch|endpoint|api_view)[\\s\\S]*")
  AND NOT ANY(d IN f.decorators WHERE toLower(d) =~ "[\\s\\S]*(login_required|auth|permission|protect|jwt|token|require)[\\s\\S]*")
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Identifies HTTP route handlers that lack authentication "
            "or authorization decorators."
        ),
    ),
    # ── Path Traversal ────────────────────────────────────────────────
    SecurityQuery(
        id="path_traversal",
        category="Path Traversal",
        severity="high",
        title="Potential Path Traversal",
        cypher=r"""
MATCH (f:Function)
WHERE f.source_code IS NOT NULL
  AND f.source_code =~ "[\\s\\S]*open\\([\\s\\S]*\\+[\\s\\S]*\\)[\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Detects file open() calls that use string concatenation, "
            "which may be vulnerable to path traversal attacks."
        ),
    ),
    # ── Unsafe Deserialization ────────────────────────────────────────
    SecurityQuery(
        id="unsafe_deserialization",
        category="Unsafe Deserialization",
        severity="critical",
        title="Unsafe Pickle/YAML Deserialization",
        cypher=r"""
MATCH (f:Function)
WHERE f.source_code IS NOT NULL
  AND f.source_code =~ "[\\s\\S]*(pickle\\.loads?|yaml\\.load\\(|yaml\\.unsafe_load)[\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Finds dangerous deserialization using pickle.load() or "
            "yaml.load() without safe loaders."
        ),
    ),
    # ── Debug/Info Leakage ────────────────────────────────────────────
    SecurityQuery(
        id="debug_exposure",
        category="Information Exposure",
        severity="medium",
        title="Debug Mode / Stack Trace Exposure",
        cypher=r"""
MATCH (f:Function)
WHERE f.source_code IS NOT NULL
  AND toLower(f.source_code) =~ "[\\s\\S]*(debug\\s*=\\s*true|app\\.debug\\s*=\\s*true|traceback\\.print_exc|print\\([\\s\\S]*traceback)[\\s\\S]*"
RETURN f.qualified_name AS function,
       f.name AS name,
       f.start_line AS start_line,
       f.end_line AS end_line
LIMIT 50
""",
        description=(
            "Identifies debug mode enabled in production or stack traces "
            "being printed that could leak internal information."
        ),
    ),
]
