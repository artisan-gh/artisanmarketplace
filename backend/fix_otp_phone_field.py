"""
Fix: use User.phone_number instead of User.phone in OTP flows.

Also strips the installer-added `phone` field from accounts/models.py if present.
"""
from pathlib import Path
import re

ROOT = Path(".")


def patch(path, replacements, label=""):
    p = ROOT / path
    if not p.exists():
        print(f"  !!      {path} not found")
        return
    text = p.read_text(encoding="utf-8")
    changed = False
    for old, new in replacements:
        if new in text:
            continue
        if old not in text:
            print(f"  !!      {path}: marker not found for {old[:60]!r}")
            continue
        text = text.replace(old, new)
        changed = True
    if changed:
        p.write_text(text, encoding="utf-8")
        print(f"  updated {path} {label}")
    else:
        print(f"  skip    {path}")


print("\n=== Fix: OTP uses User.phone_number ===\n")

# ------------------------------------------------------------------
# 1. accounts/views_otp.py — swap phone → phone_number for User
# ------------------------------------------------------------------
print("[1/3] accounts/views_otp.py")

patch("accounts/views_otp.py", [
    # Filter existing user by phone_number
    (
        "    user = User.objects.filter(phone=phone).first()",
        "    user = User.objects.filter(phone_number=phone).first()",
    ),
    # Create user with phone_number
    (
        '''        user = User.objects.create(
            username=phone, phone=phone,
            user_type="CLIENT", is_active=True,
        )''',
        '''        user = User.objects.create(
            username=phone, phone_number=phone,
            user_type="CLIENT", is_active=True,
        )''',
    ),
    # Existing-user check in SendOTPView
    (
        "        existing = User.objects.filter(phone=phone).first()",
        "        existing = User.objects.filter(phone_number=phone).first()",
    ),
    # Response payload
    (
        '                "phone": user.phone, "user_type": user.user_type,',
        '                "phone": user.phone_number, "user_type": user.user_type,',
    ),
])

# ------------------------------------------------------------------
# 2. accounts/models.py — remove installer-added `phone` field
# ------------------------------------------------------------------
print("\n[2/3] accounts/models.py")

p = ROOT / "accounts/models.py"
if p.exists():
    text = p.read_text(encoding="utf-8")
    # Match the exact multi-line field the installer added
    pattern = (
        r'\n    phone = models\.CharField\(\n'
        r'        max_length=20, unique=True, null=True, blank=True,\n'
        r'        db_index=True,\n'
        r'        help_text="Required for CLIENT users\. Optional for staff\.",\n'
        r'    \)\n'
    )
    if re.search(pattern, text):
        text = re.sub(pattern, "\n", text, count=1)
        p.write_text(text, encoding="utf-8")
        print("  removed installer-added phone field")
    else:
        print("  skip    (no installer-added phone field to remove)")
else:
    print("  !!      accounts/models.py not found")

# ------------------------------------------------------------------
# 3. Verify
# ------------------------------------------------------------------
print("\n[3/3] Verify")
print("""
If everything worked, these should now be true:

  - accounts/views_otp.py uses User.phone_number
  - accounts/models.py has no installer-added `phone` field
  - Customer still uses `phone` (unchanged)

Next:
  python manage.py makemigrations accounts customers
  python manage.py migrate
""")