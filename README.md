# Exasol Application Challenge Solver

A Python script that automates the Exasol hiring challenge — connects to the server over TLS, solves a Proof-of-Work puzzle, and submits personal details.

## Requirements

- Python 3.7+
- TLS certificate and private key (provided in the challenge README)

## Setup

1. Create a `certs/` directory in the same folder as `solve.py`.
2. Save the certificate as `certs/client.crt` and the private key as `certs/client.key`.
3. Update the personal details at the top of `solve.py`:

```python
NAME      = "Your Full Name"
MAIL1     = "your.email@example.com"
BIRTHDATE = "DD.MM.YYYY"
COUNTRY   = "Your Country"
ADDRLINE1 = "Street and Number"
ADDRLINE2 = "City, State, ZIP"
```

## Usage

```bash
python solve.py
```

The script will:
1. Connect to the server on one of the available ports (`3336, 8083, 8446, 49155, 3481, 65532`)
2. Complete the TLS handshake (`HELO`)
3. Solve the SHA1 Proof-of-Work puzzle
4. Respond to identity questions (`NAME`, `MAIL`, `BIRTHDATE`, etc.)
5. Print `Application submitted successfully!` on success

## How It Works

The server issues a `POW` command with an `authdata` string and a `difficulty` level. The script repeatedly generates random suffixes until:

```
SHA1(authdata + suffix).startswith("0" * difficulty)
```

All other responses are HMAC-style: `SHA1(authdata + challenge_token) + " " + value`.

## Notes

- The POW timeout is **2 hours**; all other commands time out in **6 seconds**.
- Suffix characters must be valid UTF-8, excluding `\n`, `\r`, `\t`, and space.
- The server accepts connections only with valid client certificates.
