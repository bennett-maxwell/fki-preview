#!/usr/bin/env python3
"""Blueprint Factory manifest validator.

Creates/validates a machine-readable manifest for a single Blueprint package.
It never sends email, never writes to GHL, and never approves external delivery.
"""
import argparse, datetime, hashlib, json, pathlib, subprocess, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def http_readback(url: str, expected_sha = None):
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            body = r.read()
            actual = hashlib.sha256(body).hexdigest()
            return {
                'url': url,
                'http_code': getattr(r, 'status', 0),
                'size_download': len(body),
                'sha256': actual,
                'sha_match': (not expected_sha) or actual == expected_sha,
                'pass': getattr(r, 'status', 0) == 200 and ((not expected_sha) or actual == expected_sha),
            }
    except Exception as exc:
        return {'url': url, 'http_code': 0, 'error': str(exc), 'pass': False}


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {'cmd': cmd, 'returncode': p.returncode, 'stdout_tail': p.stdout.splitlines()[-20:], 'stderr_tail': p.stderr.splitlines()[-20:], 'pass': p.returncode == 0}


def validate_token(token_path, lead, html, email, profile, receipt_dir):
    return run([sys.executable, 'scripts/blueprint_gatekeeper_100.py', '--verify-token', '--lead', lead, '--html', str(html.relative_to(ROOT)), '--receipt-dir', str(receipt_dir.relative_to(ROOT)), '--delivery-email', str(email.relative_to(ROOT)), '--profile', str(profile.relative_to(ROOT)), '--token', str(token_path.relative_to(ROOT)), '--json-output'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lead', required=True)
    ap.add_argument('--write', action='store_true', help='write manifest to audit-receipts/<lead>/<lead>-factory-manifest.json')
    ap.add_argument('--public-podcast-url')
    ap.add_argument('--bennett-approval-receipt')
    args = ap.parse_args()

    lead = args.lead
    receipt_dir = ROOT / 'audit-receipts' / lead
    html = ROOT / 'blueprints' / f'{lead}.html'
    email = ROOT / 'delivery-emails' / f'{lead}-delivery-email.html'
    profile = ROOT / 'leads' / f'{lead}.json'
    prod47 = receipt_dir / f'{lead}-production-47.json'
    token = receipt_dir / f'{lead}-gatekeeper-pass-token.json'

    artifacts = {name: path for name, path in {
        'blueprint_html': html,
        'delivery_email': email,
        'lead_profile': profile,
        'production_47': prod47,
        'gatekeeper_token': token,
    }.items()}
    manifest = {
        'schema': 'blueprint_factory_manifest.v1',
        'lead': lead,
        'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'artifacts': {},
        'gates': {},
        'send_lock': {
            'bennett_preview_allowed': False,
            'external_send_allowed': False,
            'external_send_block_reason': 'not_evaluated',
        },
        'status': 'FAIL',
        'failures': [],
    }

    for name, path in artifacts.items():
        exists = path.exists()
        manifest['artifacts'][name] = {'path': str(path), 'exists': exists}
        if exists:
            manifest['artifacts'][name].update({'size_bytes': path.stat().st_size, 'sha256': sha(path)})
        else:
            manifest['failures'].append(f'missing artifact: {name} {path}')

    prod = load_json(prod47) if prod47.exists() else None
    if isinstance(prod, dict):
        manifest['gates']['production_47_schema'] = {
            'pass': prod.get('pass') is True and prod.get('http_code') == 200 and int(prod.get('size_download') or 0) > 0 and prod.get('audio_sha256') == prod.get('public_sha256'),
            'audio_sha256': prod.get('audio_sha256'),
            'public_sha256': prod.get('public_sha256'),
            'http_code': prod.get('http_code'),
            'size_download': prod.get('size_download'),
        }
    else:
        manifest['gates']['production_47_schema'] = {'pass': False}

    if args.public_podcast_url and isinstance(prod, dict):
        manifest['gates']['public_podcast_readback'] = http_readback(args.public_podcast_url, prod.get('audio_sha256'))

    manifest['gates']['run_audit'] = run([sys.executable, 'run-audit.py', '--lead', lead])
    manifest['gates']['completion_gate'] = run([sys.executable, 'scripts/blueprint_completion_gate.py', '--html', str(html.relative_to(ROOT)), '--receipt-dir', str(receipt_dir.relative_to(ROOT)), '--lead', lead, '--require-production', '--json-output'])
    manifest['gates']['qualify_link_gate'] = run([sys.executable, 'scripts/blueprint_qualify_link_gate.py', '--html', str(html.relative_to(ROOT)), '--check-http', '--json-output'])
    manifest['gates']['qualifier_context_gate'] = run([sys.executable, 'scripts/blueprint_qualifier_context_gate.py', '--html', str(html.relative_to(ROOT)), '--delivery-email', str(email.relative_to(ROOT)), '--profile', str(profile.relative_to(ROOT)), '--lead', lead, '--json-output'])
    manifest['gates']['approval_email_customer_view_gate'] = run([sys.executable, 'scripts/blueprint_approval_email_gate.py', '--email', str(email.relative_to(ROOT)), '--profile', str(profile.relative_to(ROOT)), '--json-output'])
    manifest['gates']['email_visual_format_gate'] = run([sys.executable, 'scripts/blueprint_email_visual_gate.py', '--email', str(email.relative_to(ROOT)), '--subject', f'CUSTOMER VIEW PREVIEW: {lead} - Your Custom Blueprint is Ready', '--json-output'])
    if token.exists() and html.exists() and email.exists() and profile.exists():
        manifest['gates']['gatekeeper_token_verify'] = validate_token(token, lead, html, email, profile, receipt_dir)
    else:
        manifest['gates']['gatekeeper_token_verify'] = {'pass': False, 'reason': 'missing token or bound artifact'}

    gate_pass = all(g.get('pass') is True for g in manifest['gates'].values())
    token_data = load_json(token) if token.exists() else None
    token_obj = token_data.get('pass_token', token_data) if isinstance(token_data, dict) else {}
    preview_allowed = gate_pass and token_obj.get('pass') is True and 'bennett_preview' in token_obj.get('allowed_actions', [])
    approval = load_json(pathlib.Path(args.bennett_approval_receipt)) if args.bennett_approval_receipt else None
    approval_ok = isinstance(approval, dict) and approval.get('external_customer_send_approved') is True and approval.get('bennett_approved') is True
    external_allowed = gate_pass and approval_ok and 'external_send' in token_obj.get('allowed_actions', [])

    manifest['send_lock'] = {
        'bennett_preview_allowed': preview_allowed,
        'external_send_allowed': external_allowed,
        'external_send_block_reason': None if external_allowed else 'requires current Bennett approval receipt and Gatekeeper token allowed_actions contains external_send',
        'token_allowed_actions': token_obj.get('allowed_actions', []),
        'approval_receipt_checked': bool(args.bennett_approval_receipt),
    }
    if gate_pass and preview_allowed:
        manifest['status'] = 'PASS_PREVIEW_ONLY'
    if external_allowed:
        manifest['status'] = 'PASS_EXTERNAL_SEND_ALLOWED'
    if not gate_pass:
        manifest['failures'].extend([name for name, gate in manifest['gates'].items() if gate.get('pass') is not True])

    out = receipt_dir / f'{lead}-factory-manifest.json'
    if args.write:
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest['status'].startswith('PASS') else 1

if __name__ == '__main__':
    raise SystemExit(main())
