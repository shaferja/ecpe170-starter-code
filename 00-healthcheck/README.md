# ECPE 170 Personal Linux VM Health Check

Run [`healthcheck.sh`](healthcheck.sh) inside your personal Ubuntu Linux VM after installing the complete package list from the VMware and Ubuntu Setup Guide in the course Canvas site.

```bash
cd ~/ecpe170-starter-code/00-healthcheck
bash healthcheck.sh | tee healthcheck-receipt.txt
```

Use the actual path to your starter-code checkout if it is not `~/ecpe170-starter-code`. The script uses a temporary directory for compile and import checks, removes that directory when it exits, and does not modify your project. It requires no administrator access, GPU, container, or Canvas credentials.

The check supports native AMD64 Ubuntu (`uname -m` reports `x86_64`) and native ARM64 Ubuntu (`uname -m` reports `aarch64`) without processor emulation. It also verifies that the `code` command for Visual Studio Code is installed; if that check fails, run `sudo snap install code --classic` and rerun the complete health check.

- `[PASS]` means the named required capability worked.
- `[FAIL]` means a blocking setup problem. A later pass does not cancel it.
- `RESULT: READY for ECPE 170` means the script found no blocking failures.
- `RESULT: NOT READY` means you should save the receipt, repair every failure, and rerun the complete check.

Exact version text can vary. If the result is not ready, include the complete receipt and the command you used when asking the instructor or TA for help.
