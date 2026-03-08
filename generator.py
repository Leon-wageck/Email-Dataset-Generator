#!/usr/bin/env python3
# Safe Email Generator (Synthetic/Test) — Tkinter GUI
# Features:
# - Fictional name generator (syllable-based, not real name lists)
# - Add specific names manually
# - Deduplicate names button (case-insensitive)
# - Separate seeds: name seed + email seed (reproducible)
# - Export: CSV (name,email,domain,pattern,username)
# - Domain list import/export
# - Domain generator (private provider pool)
#
# Defaults use RFC-reserved example domains. If you add domains, only use domains you control.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import re
import json
from datetime import datetime
from typing import List, Dict, Any

# RFC 2606 reserved example domains (safe for testing)
DEFAULT_DOMAINS = ["gmail.com", "example.org", "example.net"]

# Built-in pool of common private email provider domains
# Use these only if appropriate for your testing workflow.
PROVIDER_DOMAINS = [
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "hotmail.co.uk",
    "hotmail.de",
    "live.com",
    "live.co.uk",
    "msn.com",
    "icloud.com",
    "me.com",
    "mac.com",
    "yahoo.com",
    "yahoo.co.uk",
    "yahoo.de",
    "yahoo.fr",
    "yahoo.ca",
    "yahoo.com.au",
    "yahoo.co.in",
    "aol.com",
    "aim.com",
    "mail.com",
    "email.com",
    "usa.com",
    "post.com",
    "consultant.com",
    "techie.com",
    "engineer.com",
    "accountant.com",
    "proton.me",
    "protonmail.com",
    "pm.me",
    "tutanota.com",
    "tuta.io",
    "tutamail.com",
    "mailbox.org",
    "posteo.de",
    "runbox.com",
    "fastmail.com",
    "fastmail.fm",
    "fastmail.com.au",
    "gmx.de",
    "gmx.net",
    "gmx.com",
    "web.de",
    "freenet.de",
    "t-online.de",
    "arcor.de",
    "vodafone.de",
    "unitybox.de",
    "1und1.de",
    "ionos.de",
    "mail.de",
    "email.de",
    "online.de",
    "netcologne.de",
    "kabelmail.de",
    "versanet.de",
    "o2online.de",
    "laposte.net",
    "orange.fr",
    "wanadoo.fr",
    "free.fr",
    "sfr.fr",
    "bbox.fr",
    "neuf.fr",
    "alice.it",
    "libero.it",
    "virgilio.it",
    "tin.it",
    "tiscali.it",
    "fastwebnet.it",
    "yandex.com",
    "yandex.ru",
    "yandex.by",
    "yandex.kz",
    "mail.ru",
    "bk.ru",
    "inbox.ru",
    "list.ru",
    "ukr.net",
    "meta.ua",
    "i.ua",
    "seznam.cz",
    "centrum.cz",
    "atlas.cz",
    "volny.cz",
    "email.cz",
    "abv.bg",
    "mail.bg",
    "dir.bg",
    "interia.pl",
    "wp.pl",
    "onet.pl",
    "o2.pl",
    "gazeta.pl",
    "poczta.fm",
    "poczta.onet.pl",
    "rediffmail.com",
    "rediff.com",
    "india.com",
    "sify.com",
    "indiatimes.com",
    "in.com",
    "rocketmail.com",
    "zoho.com",
    "zohomail.com",
    "mailfence.com",
    "hushmail.com",
    "countermail.com",
    "startmail.com",
    "kolabnow.com",
    "disroot.org",
    "riseup.net",
    "mailbox.com",
    "vfemail.net",
    "lycos.com",
    "lycos.de",
    "excite.com",
    "excite.it",
    "netscape.net",
    "juno.com",
    "netzero.com",
    "bigpond.com",
    "telstra.com",
    "optusnet.com.au",
    "ii.net",
    "internode.on.net",
    "btinternet.com",
    "sky.com",
    "talktalk.net",
    "virginmedia.com",
    "blueyonder.co.uk",
    "ntlworld.com",
    "plus.net",
    "orange.net",
    "wanadoo.co.uk",
    "btopenworld.com",
    "mail.ee",
    "hot.ee",
    "mail.lv",
    "inbox.lv",
    "inbox.lt",
    "mail.lt",
    "one.lt",
    "email.it",
    "mail.dk",
    "post.dk",
    "webmail.co.za",
    "mweb.co.za",
    "telkomsa.net",
    "vodamail.co.za",
    "terra.com",
    "terra.es",
    "terra.com.br",
    "bol.com.br",
    "uol.com.br",
    "ig.com.br",
    "r7.com",
    "globo.com",
    "hotmail.com.br",
    "yahoo.com.br",
    "clix.pt",
    "sapo.pt",
    "mail.pt",
    "iol.pt",
    "mail.gr",
    "otenet.gr",
    "forthnet.gr",
    "hol.gr",
    "cytanet.com.cy",
    "cytanet.com",
]

PATTERNS = [
    "{first}.{last}",
    "{first}{last}",
    "{f}{last}",
    "{first}{l}",
    "{last}.{first}",
    "{first}_{last}",
    "{first}-{last}",
    "{first}.{last}{n2}",
    "{first}{last}{n3}",
]

# Fictional syllables (not sourced from real-name lists)
FIRST_SYLLABLES = [
    "al", "an", "ar", "be", "ca", "da", "el", "fa", "jo", "ka",
    "li", "ma", "na", "or", "pa", "ra", "sa", "ta", "ve", "za",
    "mi", "no", "ri", "lu", "ke", "ti"
]
MIDDLE_SYLLABLES = ["la", "re", "mi", "no", "ta", "di", "ko", "vi", "ra", "lo", "ne", ""]
LAST_SYLLABLES = ["son", "ner", "lin", "mar", "ton", "ric", "ven", "ley", "dan", "tis", "mond", "berg", "stone"]

def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s

def split_name(full: str):
    parts = [p for p in re.split(r"\s+", full.strip()) if p]
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], "user"
    return parts[0], parts[-1]

def fictional_name(rng: random.Random) -> str:
    first = (rng.choice(FIRST_SYLLABLES) + rng.choice(MIDDLE_SYLLABLES)).capitalize()
    last = (rng.choice(FIRST_SYLLABLES) + rng.choice(MIDDLE_SYLLABLES) + rng.choice(LAST_SYLLABLES)).capitalize()
    first = re.sub(r"[^A-Za-z]+", "", first) or "Alex"
    last = re.sub(r"[^A-Za-z]+", "", last) or "River"
    return f"{first} {last}"

def render_pattern(pattern: str, first: str, last: str, rng: random.Random) -> str:
    f = first[:1]
    l = last[:1]
    n2 = f"{rng.randint(0, 99):02d}"
    n3 = f"{rng.randint(0, 999):03d}"
    return pattern.format(first=first, last=last, f=f, l=l, n2=n2, n3=n3)

def normalize_name_line(line: str) -> str:
    # Trim + collapse whitespace
    line = re.sub(r"\s+", " ", line.strip())
    return line

def normalize_domain_line(line: str) -> str:
    # Trim + lowercase
    return line.strip().lower()

def sql_escape(s: str) -> str:
    # Basic SQL string literal escape
    return s.replace("'", "''")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Safe Email Generator (Synthetic/Test)")
        self.geometry("1120x780")

        # Stores most recent generated rows for export
        self.last_rows: List[Dict[str, Any]] = []

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        warning = (
            "Synthetic/test data only. Defaults use example domains. "
            "If you add domains, only use domains you control."
        )
        ttk.Label(top, text=warning, foreground="#8a1f11").pack(anchor="w", pady=(0, 8))

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = ttk.Frame(main)
        right.pack(side="right", fill="both", expand=True)

        # ---------- Names ----------
        names_frame = ttk.LabelFrame(left, text="Names (add your own + generate fictional)", padding=8)
        names_frame.pack(fill="both", expand=True)

        names_controls = ttk.Frame(names_frame)
        names_controls.pack(fill="x", pady=(0, 6))

        ttk.Label(names_controls, text="Name seed:").pack(side="left")
        self.name_seed_var = tk.StringVar(value="")
        ttk.Entry(names_controls, textvariable=self.name_seed_var, width=18).pack(side="left", padx=(6, 12))

        ttk.Label(names_controls, text="Generate names:").pack(side="left")
        self.gen_names_count_var = tk.StringVar(value="200")
        ttk.Entry(names_controls, textvariable=self.gen_names_count_var, width=8).pack(side="left", padx=(6, 6))

        self.gen_mode_var = tk.StringVar(value="append")
        ttk.Radiobutton(names_controls, text="Append", variable=self.gen_mode_var, value="append").pack(side="left", padx=6)
        ttk.Radiobutton(names_controls, text="Replace", variable=self.gen_mode_var, value="replace").pack(side="left", padx=6)

        ttk.Button(names_controls, text="Generate", command=self.generate_names).pack(side="left", padx=(12, 6))
        ttk.Button(names_controls, text="Deduplicate Names", command=self.dedup_names).pack(side="left")

        add_frame = ttk.Frame(names_frame)
        add_frame.pack(fill="x", pady=(0, 6))
        ttk.Label(add_frame, text='Add specific name (e.g. "Max Example"):').pack(side="left")
        self.add_name_var = tk.StringVar(value="")
        ttk.Entry(add_frame, textvariable=self.add_name_var).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(add_frame, text="Add", command=self.add_name).pack(side="left")

        self.names_text = tk.Text(names_frame, height=16, wrap="none")
        self.names_text.pack(fill="both", expand=True)
        self.names_text.insert("1.0", "")

        # ---------- Domains ----------
        domains_frame = ttk.LabelFrame(left, text="Domains (safe defaults)", padding=8)
        domains_frame.pack(fill="both", expand=False, pady=(10, 0))

        domains_controls = ttk.Frame(domains_frame)
        domains_controls.pack(fill="x", pady=(0, 6))

        ttk.Label(domains_controls, text="Domain seed:").pack(side="left")
        self.domain_seed_var = tk.StringVar(value="")
        ttk.Entry(domains_controls, textvariable=self.domain_seed_var, width=18).pack(side="left", padx=(6, 12))

        ttk.Label(domains_controls, text="Generate domains:").pack(side="left")
        self.gen_domains_count_var = tk.StringVar(value="25")
        ttk.Entry(domains_controls, textvariable=self.gen_domains_count_var, width=8).pack(side="left", padx=(6, 6))

        self.domain_gen_mode_var = tk.StringVar(value="append")
        ttk.Radiobutton(domains_controls, text="Append", variable=self.domain_gen_mode_var, value="append").pack(side="left", padx=6)
        ttk.Radiobutton(domains_controls, text="Replace", variable=self.domain_gen_mode_var, value="replace").pack(side="left", padx=6)

        ttk.Button(domains_controls, text="Generate Domains", command=self.generate_domains).pack(side="left", padx=(12, 6))
        ttk.Button(domains_controls, text="Deduplicate Domains", command=self.dedup_domains).pack(side="left", padx=(6, 0))

        domains_io = ttk.Frame(domains_frame)
        domains_io.pack(fill="x", pady=(0, 6))
        ttk.Button(domains_io, text="Import Domains", command=self.import_domains).pack(side="left")
        ttk.Button(domains_io, text="Export Domains", command=self.export_domains).pack(side="left", padx=8)

        self.domains_text = tk.Text(domains_frame, height=8, wrap="none")
        self.domains_text.pack(fill="both", expand=True)
        self.domains_text.insert("1.0", "\n".join(DEFAULT_DOMAINS))

        # ---------- Settings ----------
        controls = ttk.LabelFrame(right, text="Email Generation Settings", padding=10)
        controls.pack(fill="x")

        row0 = ttk.Frame(controls)
        row0.pack(fill="x")

        ttk.Label(row0, text="Email seed:").pack(side="left")
        self.email_seed_var = tk.StringVar(value="")
        ttk.Entry(row0, textvariable=self.email_seed_var, width=18).pack(side="left", padx=(6, 12))

        ttk.Label(row0, text="Email count:").pack(side="left")
        self.count_var = tk.StringVar(value="200")
        ttk.Entry(row0, textvariable=self.count_var, width=10).pack(side="left", padx=8)

        self.unique_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row0, text="Unique", variable=self.unique_var).pack(side="left", padx=10)

        self.lower_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row0, text="Lowercase", variable=self.lower_var).pack(side="left", padx=10)

        # Patterns
        pats = ttk.LabelFrame(controls, text="Patterns", padding=8)
        pats.pack(fill="x", pady=(10, 0))

        self.pattern_vars = []
        grid = ttk.Frame(pats)
        grid.pack(fill="x")

        for i, p in enumerate(PATTERNS):
            v = tk.BooleanVar(value=True if i < 6 else False)
            self.pattern_vars.append((p, v))
            ttk.Checkbutton(grid, text=p, variable=v).grid(row=i // 2, column=i % 2, sticky="w", padx=8, pady=2)

        # Buttons: generate + export
        btns = ttk.Frame(right, padding=(0, 10))
        btns.pack(fill="x")

        ttk.Button(btns, text="Generate Emails", command=self.generate_emails).pack(side="left")
        ttk.Button(btns, text="Copy Output", command=self.copy).pack(side="left", padx=8)
        ttk.Button(btns, text="Save Output .txt", command=self.save_txt).pack(side="left", padx=8)
        ttk.Button(btns, text="Clear Output", command=lambda: self.out.delete("1.0", "end")).pack(side="left", padx=8)

        export = ttk.LabelFrame(right, text="Structured Export (from last generated emails)", padding=10)
        export.pack(fill="x", pady=(0, 10))

        exp_btns = ttk.Frame(export)
        exp_btns.pack(fill="x")

        ttk.Button(exp_btns, text="Export CSV", command=self.export_csv).pack(side="left")
        ttk.Button(exp_btns, text="Export JSON", command=self.export_json).pack(side="left", padx=8)
        ttk.Button(exp_btns, text="Export SQL", command=self.export_sql).pack(side="left", padx=8)

        ttk.Label(export, text="(Exports include: name, email, domain, pattern, username)").pack(anchor="w", pady=(6, 0))

        # Output
        out_frame = ttk.LabelFrame(right, text="Output (emails)", padding=8)
        out_frame.pack(fill="both", expand=True)

        self.out = tk.Text(out_frame, wrap="none")
        self.out.pack(fill="both", expand=True)

    def _read_lines(self, widget: tk.Text) -> List[str]:
        raw = widget.get("1.0", "end").splitlines()
        return [normalize_name_line(ln) for ln in raw if normalize_name_line(ln)]

    def _read_domain_lines(self, widget: tk.Text) -> List[str]:
        raw = widget.get("1.0", "end").splitlines()
        return [normalize_domain_line(ln) for ln in raw if normalize_domain_line(ln)]

    def _rng_from_seed(self, seed_value: str) -> random.Random:
        seed_value = seed_value.strip()
        return random.Random(seed_value if seed_value != "" else None)

    def add_name(self):
        name = normalize_name_line(self.add_name_var.get())
        if not name:
            return
        if len(re.sub(r"[^A-Za-z]", "", name)) < 2:
            messagebox.showerror("Invalid name", 'Please enter a plausible name like "Max Example".')
            return

        current = self.names_text.get("1.0", "end").strip()
        if current:
            self.names_text.insert("end", "\n" + name)
        else:
            self.names_text.insert("1.0", name)

        self.add_name_var.set("")

    def dedup_names(self):
        lines = self._read_lines(self.names_text)
        seen = set()
        out = []
        for ln in lines:
            key = ln.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(ln)
        self.names_text.delete("1.0", "end")
        self.names_text.insert("1.0", "\n".join(out))
        messagebox.showinfo("Deduplicate", f"Kept {len(out)} unique names.")

    def dedup_domains(self):
        lines = self._read_domain_lines(self.domains_text)
        seen = set()
        out = []
        for ln in lines:
            key = ln.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(ln)
        self.domains_text.delete("1.0", "end")
        self.domains_text.insert("1.0", "\n".join(out))
        messagebox.showinfo("Deduplicate", f"Kept {len(out)} unique domains.")

    def generate_names(self):
        try:
            n = int(self.gen_names_count_var.get().strip())
            if n <= 0 or n > 200000:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid count", "Name count must be an integer between 1 and 200000.")
            return

        rng = self._rng_from_seed(self.name_seed_var.get())

        names = [fictional_name(rng) for _ in range(n)]

        if self.gen_mode_var.get() == "replace":
            self.names_text.delete("1.0", "end")
            self.names_text.insert("1.0", "\n".join(names))
        else:
            existing = self.names_text.get("1.0", "end").strip()
            if existing:
                self.names_text.insert("end", "\n" + "\n".join(names))
            else:
                self.names_text.insert("1.0", "\n".join(names))

    def generate_domains(self):
        try:
            n = int(self.gen_domains_count_var.get().strip())
            if n <= 0 or n > len(PROVIDER_DOMAINS):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid count",
                f"Domain count must be an integer between 1 and {len(PROVIDER_DOMAINS)}."
            )
            return

        rng = self._rng_from_seed(self.domain_seed_var.get())
        domains = rng.sample(PROVIDER_DOMAINS, n)

        if self.domain_gen_mode_var.get() == "replace":
            self.domains_text.delete("1.0", "end")
            self.domains_text.insert("1.0", "\n".join(domains))
        else:
            existing = self.domains_text.get("1.0", "end").strip()
            if existing:
                self.domains_text.insert("end", "\n" + "\n".join(domains))
            else:
                self.domains_text.insert("1.0", "\n".join(domains))

    def import_domains(self):
        path = filedialog.askopenfilename(
            title="Import Domains",
            filetypes=[
                ("Text/CSV files", "*.txt *.csv"),
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Import failed", f"Could not read file:\n{e}")
            return

        # Accept newline, comma, semicolon, tab, and whitespace-separated input
        parts = re.split(r"[\n\r,;\t ]+", content)
        domains = [normalize_domain_line(p) for p in parts if normalize_domain_line(p)]

        if not domains:
            messagebox.showerror("Import failed", "No domains found in file.")
            return

        current = self.domains_text.get("1.0", "end").strip()
        if current:
            self.domains_text.insert("end", "\n" + "\n".join(domains))
        else:
            self.domains_text.insert("1.0", "\n".join(domains))

        messagebox.showinfo("Imported", f"Imported {len(domains)} domain entries.")

    def export_domains(self):
        domains = self._read_domain_lines(self.domains_text)
        if not domains:
            messagebox.showerror("Nothing to export", "No domains to export.")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"domains_{ts}.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(domains) + "\n")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not write file:\n{e}")
            return

        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    def generate_emails(self):
        rng = self._rng_from_seed(self.email_seed_var.get())

        try:
            count = int(self.count_var.get().strip())
            if count <= 0 or count > 200000:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid count", "Email count must be an integer between 1 and 200000.")
            return

        names = self._read_lines(self.names_text)
        domains = self._read_domain_lines(self.domains_text)

        if not names:
            messagebox.showerror("No names", "Add some names or click Generate in the names section.")
            return
        if not domains:
            messagebox.showerror("No domains", "Please provide at least one domain.")
            return

        bad = [d for d in domains if not re.fullmatch(r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", d)]
        if bad:
            messagebox.showerror("Invalid domains", "These domains look invalid:\n" + "\n".join(bad))
            return

        enabled_patterns = [p for (p, v) in self.pattern_vars if v.get()]
        if not enabled_patterns:
            messagebox.showerror("No patterns", "Enable at least one pattern.")
            return

        # Build parsed name pool (keep original display name too)
        name_pool = []
        for full in names:
            first, last = split_name(full)
            if not first or not last:
                continue
            first_s = slug(first)
            last_s = slug(last)
            if first_s and last_s:
                name_pool.append((full, first_s, last_s))

        if not name_pool:
            messagebox.showerror("Invalid names", 'Could not parse names. Use format like "Alex River".')
            return

        results = []
        rows: List[Dict[str, Any]] = []
        seen = set()

        max_tries = count * (10 if self.unique_var.get() else 2)
        tries = 0

        while len(results) < count and tries < max_tries:
            tries += 1
            display_name, first, last = rng.choice(name_pool)
            pattern = rng.choice(enabled_patterns)
            username = render_pattern(pattern, first, last, rng)

            if self.lower_var.get():
                username = username.lower()

            username = re.sub(r"[^a-z0-9._-]+", "", username)
            username = re.sub(r"[._-]{2,}", ".", username).strip(".-_")
            if not username or len(username) < 3:
                continue

            domain = rng.choice(domains).lower()
            email = f"{username}@{domain}"

            if self.unique_var.get():
                if email in seen:
                    continue
                seen.add(email)

            results.append(email)
            rows.append({
                "name": display_name,
                "email": email,
                "domain": domain,
                "pattern": pattern,
                "username": username,
            })

        if len(results) < count:
            messagebox.showwarning(
                "Generated fewer than requested",
                f"Requested {count}, generated {len(results)}. "
                f"Try adding more names/domains, enabling more patterns, or disabling uniqueness."
            )

        self.last_rows = rows

        self.out.delete("1.0", "end")
        self.out.insert("1.0", "\n".join(results))

    def copy(self):
        data = self.out.get("1.0", "end").strip()
        if not data:
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        messagebox.showinfo("Copied", "Output copied to clipboard.")

    def save_txt(self):
        data = self.out.get("1.0", "end").strip()
        if not data:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"synthetic_emails_{ts}.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(data + "\n")
        messagebox.showinfo("Saved", f"Saved to:\n{path}")

    def _ensure_rows(self) -> bool:
        if not self.last_rows:
            messagebox.showerror("Nothing to export", "Generate emails first (Generate Emails).")
            return False
        return True

    def export_csv(self):
        if not self._ensure_rows():
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"synthetic_emails_{ts}.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        headers = ["name", "email", "domain", "pattern", "username"]

        def csv_quote(val: str) -> str:
            val = "" if val is None else str(val)
            if any(ch in val for ch in [",", '"', "\n", "\r"]):
                val = '"' + val.replace('"', '""') + '"'
            return val

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(",".join(headers) + "\n")
            for r in self.last_rows:
                f.write(",".join(csv_quote(r[h]) for h in headers) + "\n")

        messagebox.showinfo("Exported CSV", f"Saved to:\n{path}")

    def export_json(self):
        if not self._ensure_rows():
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"synthetic_emails_{ts}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.last_rows, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Exported JSON", f"Saved to:\n{path}")

    def export_sql(self):
        if not self._ensure_rows():
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            initialfile=f"synthetic_emails_{ts}.sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        if not path:
            return

        table = "synthetic_emails"
        cols = ["name", "email", "domain", "pattern", "username"]

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"-- Synthetic/test data export\n")
            f.write(f"-- Table: {table}\n\n")
            f.write(f"CREATE TABLE IF NOT EXISTS {table} (\n")
            f.write("  name TEXT,\n  email TEXT,\n  domain TEXT,\n  pattern TEXT,\n  username TEXT\n")
            f.write(");\n\n")
            f.write(f"INSERT INTO {table} (name, email, domain, pattern, username) VALUES\n")

            values = []
            for r in self.last_rows:
                vals = ", ".join("'" + sql_escape(str(r[c])) + "'" for c in cols)
                values.append(f"  ({vals})")

            f.write(",\n".join(values) + ";\n")

        messagebox.showinfo("Exported SQL", f"Saved to:\n{path}")

if __name__ == "__main__":
    try:
        import tkinter  # noqa: F401
    except Exception:
        raise SystemExit("Tkinter not available. On Linux install python3-tk.")
    App().mainloop()
