import asyncio
import logging
import os
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("turboprivate.infra")


class BackupManager:
    def __init__(self, backup_path: Path = Path("./data/backups")):
        self.backup_path = backup_path
        backup_path.mkdir(parents=True, exist_ok=True)

    async def create(
        self,
        name: str,
        encrypt: bool = False,
        passphrase: str | None = None,
    ) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{timestamp}"
        backup_dir = self.backup_path / backup_name
        backup_dir.mkdir(exist_ok=True)
        kubeconfig = Path("kubeconfig.yaml")
        if kubeconfig.exists():
            (backup_dir / "kubeconfig.yaml").write_text(
                kubeconfig.read_text()
            )
        config = Path("turboprivate.yaml")
        if config.exists():
            (backup_dir / "turboprivate.yaml").write_text(
                config.read_text()
            )
        try:
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "get",
                "all",
                "--all-namespaces",
                "-o",
                "yaml",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            (backup_dir / "cluster_resources.yaml").write_text(
                stdout.decode()
            )
        except OSError as e:
            logger.warning(
                "Could not backup Kubernetes resources: %s", e
            )
        tarball = self.backup_path / f"{backup_name}.tar.gz"
        with tarfile.open(tarball, "w:gz") as tar:
            tar.add(backup_dir, arcname=backup_name)
        import shutil

        shutil.rmtree(backup_dir)
        if encrypt:
            encrypted_path = (
                self.backup_path / f"{backup_name}.tar.gz.age"
            )
            pw = passphrase or os.environ.get(
                "TURBO_BACKUP_PASS", ""
            )
            if pw:
                proc = await asyncio.create_subprocess_exec(
                    "age",
                    "--passphrase",
                    "--output",
                    str(encrypted_path),
                    str(tarball),
                    stdin=asyncio.subprocess.PIPE,
                )
                await proc.communicate(input=pw.encode())
                if proc.returncode == 0:
                    tarball.unlink()
                    return encrypted_path
        return tarball

    async def restore(
        self, name: str, target: Path | None = None
    ):
        backup_file = self.backup_path / name
        if not backup_file.exists():
            backup_file = self.backup_path / f"{name}.tar.gz"
        if not backup_file.exists():
            backup_file = self.backup_path / f"{name}.tar.gz.age"
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {name}")
        restore_dir = target or Path("./restore")
        restore_dir.mkdir(exist_ok=True)
        if backup_file.suffix == ".age":
            pw = os.environ.get("TURBO_BACKUP_PASS", "")
            proc = await asyncio.create_subprocess_exec(
                "age",
                "--decrypt",
                "--output",
                str(restore_dir / "backup.tar.gz"),
                str(backup_file),
                stdin=asyncio.subprocess.PIPE,
            )
            await proc.communicate(input=pw.encode())
            tar_path = restore_dir / "backup.tar.gz"
        else:
            tar_path = backup_file
        # Use filter='data' on Python 3.12+ (CVE-2007-4559)
        with tarfile.open(tar_path, "r:gz") as tar:
            if sys.version_info >= (3, 12):
                tar.extractall(path=restore_dir, filter="data")
            else:
                tar.extractall(path=restore_dir)  # noqa: S202
        stem = Path(backup_file.stem).stem
        kubeconfig = restore_dir / stem / "kubeconfig.yaml"
        if kubeconfig.exists():
            Path("kubeconfig.yaml").write_text(
                kubeconfig.read_text()
            )

    async def list_backups(self) -> list[dict]:
        backups = []
        for f in sorted(self.backup_path.glob("*.tar.gz*")):
            stat = f.stat()
            backups.append(
                {
                    "name": f.name,
                    "path": str(f),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(
                        stat.st_mtime, tz=UTC
                    ).isoformat(),
                    "encrypted": f.suffix == ".age",
                }
            )
        return backups

    async def verify(self, name: str) -> bool:
        backup_file = self.backup_path / name
        if not backup_file.exists():
            backup_file = self.backup_path / f"{name}.tar.gz"
        if not backup_file.exists():
            return False
        try:
            with tarfile.open(backup_file, "r:gz") as tar:
                members = tar.getmembers()
            return len(members) > 0
        except Exception as e:
            logger.warning(
                "Backup verification failed for %s: %s", name, e
            )
            return False
