import re
from typing import List, Dict, Any

PATTERNS = [
    {
        "id": "reentrancy",
        "name": "Reentrancy",
        "severity": "critical",
        "regex": r"\.call\s*\{[^}]*value\s*:",
        "description": "External call with ETH value before state update — classic reentrancy vector",
        "recommendation": "Use ReentrancyGuard or checks-effects-interactions: update state BEFORE external call"
    },
    {
        "id": "unchecked_call",
        "name": "Unchecked Return Value",
        "severity": "high",
        "regex": r"[^(bool\s\w,)]\s*\.call\s*[\(\{]",
        "description": "Return value of .call() is not checked — silent failures possible",
        "recommendation": "Always check: (bool success,) = addr.call(...); require(success, 'call failed');"
    },
    {
        "id": "tx_origin",
        "name": "tx.origin Authentication",
        "severity": "high",
        "regex": r"tx\.origin",
        "description": "tx.origin used for authorization — vulnerable to phishing/relay attacks",
        "recommendation": "Replace tx.origin with msg.sender for all authentication checks"
    },
    {
        "id": "selfdestruct",
        "name": "Selfdestruct",
        "severity": "critical",
        "regex": r"selfdestruct\s*\(",
        "description": "Contract can be permanently destroyed, sending all ETH to arbitrary address",
        "recommendation": "Remove selfdestruct or protect with multi-sig and timelock"
    },
    {
        "id": "delegatecall",
        "name": "Unsafe Delegatecall",
        "severity": "critical",
        "regex": r"delegatecall\s*\(",
        "description": "delegatecall executes foreign code in caller's storage context — storage collision risk",
        "recommendation": "Ensure delegatecall target is a trusted, immutable, audited contract"
    },
    {
        "id": "timestamp",
        "name": "Timestamp Dependence",
        "severity": "medium",
        "regex": r"block\.timestamp|(?<!\w)now(?!\w)",
        "description": "Miners can manipulate block.timestamp by up to ±15 seconds",
        "recommendation": "Do not use block.timestamp for randomness, lotteries, or critical timing windows"
    },
    {
        "id": "integer_overflow",
        "name": "Integer Overflow/Underflow",
        "severity": "high",
        "regex": r"pragma\s+solidity\s+[\^<]?\s*0\.[0-7]\.",
        "description": "Solidity <0.8.0 has no built-in overflow/underflow protection",
        "recommendation": "Upgrade to Solidity ^0.8.0 or use OpenZeppelin SafeMath library"
    },
    {
        "id": "block_number",
        "name": "Block Number Dependence",
        "severity": "low",
        "regex": r"block\.number",
        "description": "block.number can be used to predict future values — weak randomness source",
        "recommendation": "Use Chainlink VRF or commit-reveal scheme for randomness"
    },
    {
        "id": "assembly",
        "name": "Inline Assembly",
        "severity": "medium",
        "regex": r"\bassembly\s*\{",
        "description": "Inline assembly bypasses Solidity safety checks and is error-prone",
        "recommendation": "Avoid inline assembly unless absolutely necessary; document thoroughly"
    },
    {
        "id": "floating_pragma",
        "name": "Floating Pragma",
        "severity": "low",
        "regex": r"pragma\s+solidity\s+\^",
        "description": "Floating pragma allows compilation with multiple compiler versions",
        "recommendation": "Lock pragma to a specific version: pragma solidity 0.8.20;"
    }
]

def analyze_solidity(source_code: str, contract_name: str = "Contract") -> Dict[str, Any]:
    lines = source_code.split("\n")
    vulnerabilities = []
    seen_ids = set()

    for pattern in PATTERNS:
        try:
            regex = re.compile(pattern["regex"], re.IGNORECASE)
        except re.error:
            continue

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
                continue
            # Remove inline comments
            code_part = re.sub(r"//.*$", "", line)
            if regex.search(code_part) and pattern["id"] not in seen_ids:
                seen_ids.add(pattern["id"])
                vulnerabilities.append({
                    "id": pattern["id"],
                    "name": pattern["name"],
                    "severity": pattern["severity"],
                    "line": i,
                    "code_snippet": stripped[:120],
                    "description": pattern["description"],
                    "recommendation": pattern["recommendation"]
                })
                break  # one finding per pattern

    # Risk score
    score_map = {"critical": 30, "high": 20, "medium": 10, "low": 5, "info": 2}
    raw_score = sum(score_map.get(v["severity"], 0) for v in vulnerabilities)
    risk_score = min(float(raw_score), 100.0)

    severity_counts = {}
    for v in vulnerabilities:
        sev = v["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    if risk_score >= 70:
        summary = f"CRITICAL RISK — {len(vulnerabilities)} vulnerabilities detected. Do NOT deploy. Immediate remediation required."
    elif risk_score >= 40:
        summary = f"HIGH RISK — {len(vulnerabilities)} issues found. Contract should not be deployed without fixes."
    elif risk_score >= 20:
        summary = f"MEDIUM RISK — {len(vulnerabilities)} potential issues. Review and fix before production deployment."
    elif vulnerabilities:
        summary = f"LOW RISK — {len(vulnerabilities)} minor issues found. Consider fixing before deployment."
    else:
        summary = "No vulnerabilities detected. Contract appears safe based on static analysis."

    return {
        "vulnerabilities": vulnerabilities,
        "risk_score": risk_score,
        "severity_counts": severity_counts,
        "summary": summary,
        "lines_analyzed": len(lines),
        "contract_name": contract_name
    }
