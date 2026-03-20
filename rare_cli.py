import re
import subprocess
from config import RARE_BIN, CHAIN


def exec(args: list, timeout: int = 90) -> dict:
    try:
        result = subprocess.run(
            [RARE_BIN] + args,
            capture_output=True, text=True, timeout=timeout
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        return {
            "success": result.returncode == 0,
            "output": out,
            "error": err if result.returncode != 0 else "",
        }
    except FileNotFoundError:
        return {"success": False, "output": "", "error": f"rare CLI not found at {RARE_BIN}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def mint(contract: str, name: str, description: str, image_path: str,
         chain: str = CHAIN, attributes: list[tuple[str, str]] = None) -> dict:
    args = [
        "mint",
        "--contract", contract,
        "--name", name,
        "--description", description,
        "--image", image_path,
        "--chain", chain,
    ]
    for key, val in (attributes or []):
        args += ["--attribute", f"{key}={val}"]
    result = exec(args, timeout=180)
    if result["success"]:
        m = re.search(r'Token ID:\s*(\d+)', result["output"], re.IGNORECASE)
        if m:
            result["token_id"] = int(m.group(1))
    return result


def auction_create(contract: str, token_id: int, starting_price: float,
                   duration: int, chain: str = CHAIN) -> dict:
    return exec([
        "auction", "create",
        "--contract", contract,
        "--token-id", str(token_id),
        "--starting-price", str(starting_price),
        "--duration", str(duration),
        "--chain", chain,
    ], timeout=120)


def auction_bid(contract: str, token_id: int, amount: float,
                chain: str = CHAIN) -> dict:
    return exec([
        "auction", "bid",
        "--contract", contract,
        "--token-id", str(token_id),
        "--amount", str(amount),
        "--chain", chain,
    ], timeout=120)


def auction_settle(contract: str, token_id: int, chain: str = CHAIN) -> dict:
    return exec([
        "auction", "settle",
        "--contract", contract,
        "--token-id", str(token_id),
        "--chain", chain,
    ], timeout=120)


def auction_status(contract: str, token_id: int, chain: str = CHAIN) -> dict:
    return exec([
        "auction", "status",
        "--contract", contract,
        "--token-id", str(token_id),
        "--chain", chain,
    ])


def wallet_address(chain: str = CHAIN) -> str:
    result = exec(["wallet", "address", "--chain", chain])
    for line in result["output"].split("\n"):
        line = line.strip()
        if line.startswith("0x") and len(line) == 42:
            return line
    return ""
