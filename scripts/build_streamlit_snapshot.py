"""Copy the verified current study into the public Streamlit repository."""
from pathlib import Path
import hashlib
import json
import shutil

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT if (ROOT / "app.py").exists() else ROOT / "streamlit_deploy"
SNAPSHOT = DEST / "snapshot"
TEXTS = SNAPSHOT / "mda"
DOCS = DEST / "docs"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    manifest = pd.read_csv(ROOT / "data/filings_manifest.csv")
    assert len(cfg["firms"]) == 100
    assert set(manifest.ticker).issubset(cfg["firms"])
    SNAPSHOT.mkdir(exist_ok=True)
    TEXTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    copied = []
    panels = {}
    for alignment in ("same", "next", "acceptance"):
        source = ROOT / "outputs/real" / alignment
        for name, target in (("car_panel.csv", f"{alignment}_panel.csv"),
                             ("event_ar.csv", f"{alignment}_event_ar.csv"),
                             ("regressions.csv", f"{alignment}_regressions.csv")):
            shutil.copy2(source / name, SNAPSHOT / target)
            copied.append(target)
        panel = pd.read_csv(source / "car_panel.csv")
        assert len(panel) == 1000
        assert panel.accession.is_unique
        assert panel.ticker.nunique() == 100
        panels[alignment] = panel
    assert all(set(panel.accession) == set(panels["same"].accession) for panel in panels.values())

    for name, source in (
        ("sensitivity_models.csv", ROOT / "outputs/limitations/sensitivity_models.csv"),
        ("earnings_8k_flags.csv", ROOT / "data/earnings_8k_flags.csv"),
        ("filings_manifest.csv", ROOT / "data/filings_manifest.csv"),
        ("extraction_audit.csv", ROOT / "data/extraction_audit.csv"),
        ("companies_100_input.csv", ROOT / "data/companies_100_input.csv"),
        ("company_list_100_validation.csv", ROOT / "outputs/qa/company_list_100_validation.csv"),
        ("final_100_audit.json", ROOT / "outputs/qa/final_100_audit.json"),
        ("tone_panel.csv", ROOT / "data/tone_panel.csv"),
        ("exclusions.csv", ROOT / "data/exclusions.csv"),
    ):
        shutil.copy2(source, SNAPSHOT / name)
        copied.append(name)

    accessions = set().union(*(set(panel.accession) for panel in panels.values()))
    for old in TEXTS.glob("*.txt"):
        if old.stem not in accessions:
            old.unlink()
    for accession in accessions:
        source = ROOT / "data/interim/mda" / f"{accession}.txt"
        assert source.exists(), source
        shutil.copy2(source, TEXTS / source.name)
    assert len(list(TEXTS.glob("*.txt"))) == len(accessions)

    doc_names = ("REPORT", "LIMITATIONS_REMEDIATION", "LITERATURE_COMPARISON", "EXPANDED_RESULTS",
                 "REFERENCES", "DEFENSE", "METHODOLOGY", "DATA_SOURCES", "EXTRACTION_REVIEW",
                 "SAMPLE_DESIGN", "FISCAL_YEAR_REVIEW")
    for name in doc_names:
        shutil.copy2(ROOT / "docs" / f"{name}.md", DOCS / f"{name}.md")
    pdf = ROOT / "outputs/Nhom5_BaoCao.pdf"
    shutil.copy2(pdf, DEST / pdf.name)
    metadata = json.loads((ROOT / "outputs/real/run_metadata.json").read_text(encoding="utf-8"))
    payload = {
        "as_of": cfg["as_of"],
        "run_timestamp": metadata["timestamp"],
        "target_filings": 1000,
        "target_firms": 100,
        "filings": len(panels["same"]),
        "firms": int(panels["same"].ticker.nunique()),
        "fiscal_years": cfg["years"],
        "input_sha256": sha(ROOT / "data/companies_100_input.csv"),
        "source": "SEC EDGAR; frozen user-supplied 100-company list",
        "pdf_sha256": sha(DEST / pdf.name),
        "data_files": {name: sha(SNAPSHOT / name) for name in copied},
    }
    (SNAPSHOT / "metadata.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    assert not any(p.name == ".env" for p in DEST.rglob("*"))
    size = sum(p.stat().st_size for p in DEST.rglob("*") if p.is_file() and ".git" not in p.parts)
    print(f"Deployment snapshot: {len(copied)} tables, {len(accessions)} MD&A files, {size/1024**2:.1f} MiB")


if __name__ == "__main__":
    main()
