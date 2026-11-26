"""Packs the two release downloads into dist/ (reproducible: fixed timestamps, sorted entries).

  python -I tools/package_release.py

  Projectile-Self-Hit-HellForge-v<version>-build25480438.zip   the code mod: folder p11-self-hit-fast/ (sources and
                                                                manifest, no DLL; HellForge builds it)
  Projectile-Self-Hit-Options-MOM-v<version>.zip               the Mod Options Menu options pack: manifest.json and
                                                                Addon/ at the root, as Arsenal / HellForge packs are
  SHA256SUMS.txt
"""
import hashlib, json, os, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HF = os.path.join(ROOT, "hellforge")
DIST = os.path.join(ROOT, "dist")
STAMP = (2026, 1, 1, 0, 0, 0)
SKIP_DIRS = {"build", "__pycache__", ".vs", ".idea"}
SKIP_EXT = {".dll", ".pdb", ".lib", ".exp", ".obj", ".o", ".pyc", ".log"}


def files(base):
    out = []
    for root, dirs, names in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for n in sorted(names):
            if n.startswith(".") or os.path.splitext(n)[1].lower() in SKIP_EXT or n == "self-hit.ini":
                continue
            out.append(os.path.join(root, n))
    return out


def pack(zip_path, base, prefix):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files(base):
            arc = prefix + os.path.relpath(p, base).replace(os.sep, "/")
            info = zipfile.ZipInfo(arc, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(p, "rb") as f:
                z.writestr(info, f.read())
    return zip_path


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    version = json.load(open(os.path.join(HF, "p11-self-hit-fast", "hellforge-mod.json"), encoding="utf-8"))["version"]
    os.makedirs(DIST, exist_ok=True)
    outs = [
        pack(os.path.join(DIST, f"Projectile-Self-Hit-HellForge-v{version}-build25480438.zip"),
             os.path.join(HF, "p11-self-hit-fast"), "p11-self-hit-fast/"),
        pack(os.path.join(DIST, f"Projectile-Self-Hit-Options-MOM-v{version}.zip"),
             os.path.join(HF, "p11-self-hit-options"), ""),
    ]
    lines = [f"{sha256(p)}  {os.path.basename(p)}" for p in outs]
    with open(os.path.join(DIST, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    for p, line in zip(outs, lines):
        print(f"{os.path.getsize(p):>8} B  {line}")
        for n in zipfile.ZipFile(p).namelist():
            print("            ", n)


if __name__ == "__main__":
    main()
