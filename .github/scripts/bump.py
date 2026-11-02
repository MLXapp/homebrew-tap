#!/usr/bin/env python3
"""
Keeps Casks/node.rb and Casks/mlx-node.rb on the public MLX Node.

  bump.py check   -> reads https://mlx.app/api/download/mac/latest and prints version/sha256/changed for
                     $GITHUB_OUTPUT (changed=true when it differs from the casks)
  bump.py apply   -> downloads that disk image, checks its SHA-256 against what mlx.app says, and writes both casks

Both casks are written from CASK below: edit it here, never the .rb files by hand (the next run would undo it).
"""
import hashlib
import json
import os
import re
import sys
import urllib.request

LATEST = "https://mlx.app/api/download/mac/latest"
UA = "MLXapp-homebrew-tap (+https://github.com/MLXapp/homebrew-tap)"
TOKENS = ["node", "mlx-node"]

CASK = '''cask "{token}" do
  version "{version}"
  sha256 "{sha256}"

  url "https://mlx.app/api/download/mac/#{{version}}"
  name "MLX Node"
  desc "Runs AI jobs on an idle Mac for the MLX network"
  homepage "https://mlx.app/"

  livecheck do
    url "https://mlx.app/api/download/mac/latest"
    strategy :json do |json|
      json["version"]
    end
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: ">= :sonoma"

  app "MLX Node.app"

  # the same finish as `curl -fsSL mlx.app/i | sh`: no "downloaded from the Internet" question on first launch (the
  # build is notarized and its checksum is pinned above) and MLX Node opens in the menu bar
  postflight do
    system_command "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "#{{appdir}}/MLX Node.app"]
    system_command "/usr/bin/open", args: ["#{{appdir}}/MLX Node.app"] unless ENV["HOMEBREW_MLX_NO_OPEN"]
  end

  uninstall quit: "app.mlx.mac"

  zap trash: [
    "~/Library/Application Scripts/app.mlx.mac",
    "~/Library/Containers/app.mlx.mac",
  ]
end
'''


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=120)


def latest():
    with get(LATEST) as r:
        d = json.load(r)
    v, sha, url = str(d.get("version", "")), str(d.get("sha256", "")), str(d.get("url", ""))
    if not re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}", v):
        sys.exit(f"bad version from mlx.app: {v!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        sys.exit(f"bad sha256 from mlx.app: {sha!r}")
    if url != f"https://mlx.app/api/download/mac/{v}":
        sys.exit(f"unexpected url from mlx.app: {url!r}")
    return v, sha


def current():
    try:
        s = open("Casks/node.rb").read()
    except FileNotFoundError:
        return None, None
    v = re.search(r'^\s*version "([^"]+)"', s, re.M)
    h = re.search(r'^\s*sha256 "([^"]+)"', s, re.M)
    return (v.group(1) if v else None), (h.group(1) if h else None)


def out(**kv):
    lines = "".join(f"{k}={v}\n" for k, v in kv.items())
    sys.stdout.write(lines)
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(lines)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    v, sha = latest()
    cv, csha = current()
    changed = (v, sha) != (cv, csha) or any(not os.path.exists(f"Casks/{t}.rb") or open(f"Casks/{t}.rb").read() != CASK.format(token=t, version=v, sha256=sha) for t in TOKENS)
    if cmd == "check":
        out(version=v, sha256=sha, changed=str(changed).lower())
        return
    if cmd != "apply":
        sys.exit("usage: bump.py check|apply")
    # never write a checksum we didn't compute ourselves from the file Homebrew will download
    h = hashlib.sha256()
    with get(f"https://mlx.app/api/download/mac/{v}") as r:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != sha:
        sys.exit(f"sha256 mismatch for {v}: mlx.app says {sha}, the download is {h.hexdigest()}")
    os.makedirs("Casks", exist_ok=True)
    for t in TOKENS:
        with open(f"Casks/{t}.rb", "w") as f:
            f.write(CASK.format(token=t, version=v, sha256=sha))
    out(version=v, sha256=sha, changed="true")


if __name__ == "__main__":
    main()
