import asyncio
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("turboprivate.infra")


class Node:
    def __init__(
        self,
        host: str,
        user: str = "root",
        port: int = 22,
        role: str = "worker",
    ):
        self.host = host
        self.user = user
        self.port = port
        self.role = role


class ClusterConfig:
    def __init__(
        self,
        name: str = "turbo-cluster",
        provider: str = "bare-metal",
        k3s_version: str = "v1.30.0+k3s1",
        nodes: list[Node] | None = None,
        ssh_key_path: Path | None = None,
    ):
        self.name = name
        self.provider = provider
        self.k3s_version = k3s_version
        self.nodes = nodes or []
        self.ssh_key_path = ssh_key_path


class Provisioner:
    def __init__(self, config: ClusterConfig):
        self.config = config

    async def run_ssh(
        self, host: str, cmd: str, user: str = "root"
    ) -> tuple[int, str, str]:
        ssh_cmd = [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
        ]
        if self.config.ssh_key_path:
            ssh_cmd += ["-i", str(self.config.ssh_key_path)]
        ssh_cmd += [f"{user}@{host}", cmd]
        proc = await asyncio.create_subprocess_exec(
            *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode or 0, stdout.decode(), stderr.decode()

    async def provision(self, config_path: Path | None = None):
        logger.info("Provisioning cluster: %s", self.config.name)
        if self.config.provider == "bare-metal":
            await self._provision_bare_metal()
        elif self.config.provider in ("proxmox", "morpheus"):
            await self._provision_terraform()
        else:
            raise ValueError(
                f"Unsupported provider: {self.config.provider}"
            )

    async def _provision_bare_metal(self):
        if not self.config.nodes:
            raise RuntimeError(
                "No nodes configured for bare-metal provisioning"
            )
        master = next(
            (n for n in self.config.nodes if n.role == "master"),
            None,
        )
        if not master:
            raise RuntimeError("No master node configured")
        workers = [
            n for n in self.config.nodes if n.role == "worker"
        ]
        await self._install_k3s(master, workers)

    async def _provision_terraform(self):
        tf_dir = Path("./terraform")
        tf_dir.mkdir(exist_ok=True)
        tf_config = self._generate_terraform_config()
        tf_file = tf_dir / "main.tf"
        tf_file.write_text(tf_config)
        proc = await asyncio.create_subprocess_exec(
            "terraform",
            f"-chdir={tf_dir}",
            "init",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        proc = await asyncio.create_subprocess_exec(
            "terraform",
            f"-chdir={tf_dir}",
            "apply",
            "-auto-approve",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        proc = await asyncio.create_subprocess_exec(
            "terraform",
            f"-chdir={tf_dir}",
            "output",
            "-json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        outputs = json.loads(stdout)
        master_ips = outputs.get("master_ips", {}).get("value", [])
        worker_ips = outputs.get("worker_ips", {}).get("value", [])
        nodes = [Node(ip, role="master") for ip in master_ips]
        nodes += [Node(ip, role="worker") for ip in worker_ips]
        if nodes:
            self.config.nodes = nodes
            master = next(
                n for n in nodes if n.role == "master"
            )
            workers = [
                n for n in nodes if n.role == "worker"
            ]
            await self._install_k3s(master, workers)

    def _generate_terraform_config(self) -> str:
        return (
            f"# Auto-generated Terraform config for"
            f" {self.config.name}\n"
            f"# Provider: {self.config.provider}\n"
        )

    async def _install_k3s(
        self, master: Node, workers: list[Node]
    ):
        version = self.config.k3s_version
        logger.info("Installing K3s master on %s", master.host)
        install_cmd = (
            "curl -sfL https://get.k3s.io"
            f" | INSTALL_K3S_VERSION={version} sh -"
        )
        rc, _out, err = await self.run_ssh(
            master.host, install_cmd
        )
        if rc != 0:
            raise RuntimeError(
                f"K3s master install failed: {err}"
            )
        token_cmd = (
            "sudo cat /var/lib/rancher/k3s/server/node-token"
        )
        rc, out, _err = await self.run_ssh(
            master.host, token_cmd
        )
        token = out.strip()
        rc, out, _ = await self.run_ssh(
            master.host, "sudo cat /etc/rancher/k3s/k3s.yaml"
        )
        kubeconfig = out.replace("127.0.0.1", master.host)
        Path("kubeconfig.yaml").write_text(kubeconfig)
        os.environ["KUBECONFIG"] = str(
            Path("kubeconfig.yaml").absolute()
        )
        for worker in workers:
            logger.info(
                "Installing K3s worker on %s", worker.host
            )
            worker_cmd = (
                "curl -sfL https://get.k3s.io"
                f" | K3S_URL=https://{master.host}:6443"
                f" K3S_TOKEN={token}"
                f" INSTALL_K3S_VERSION={version} sh -"
            )
            rc, _out, err = await self.run_ssh(
                worker.host, worker_cmd
            )
            if rc != 0:
                logger.error(
                    "Worker %s install failed: %s",
                    worker.host,
                    err,
                )
        logger.info(
            "Cluster %s provisioned successfully",
            self.config.name,
        )

    async def destroy(self, cluster_name: str):
        logger.info("Destroying cluster: %s", cluster_name)
        if self.config.provider == "bare-metal":
            for node in self.config.nodes:
                await self.run_ssh(
                    node.host,
                    "sudo /usr/local/bin/k3s-uninstall.sh",
                )
        else:
            tf_dir = Path("./terraform")
            if tf_dir.exists():
                proc = await asyncio.create_subprocess_exec(
                    "terraform",
                    f"-chdir={tf_dir}",
                    "destroy",
                    "-auto-approve",
                )
                await proc.communicate()

    async def status(self, cluster_name: str) -> dict:
        try:
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "get",
                "nodes",
                "-o",
                "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            nodes = json.loads(stdout)
            return {
                "cluster": cluster_name,
                "status": "running",
                "node_count": len(nodes.get("items", [])),
            }
        except Exception as e:
            logger.warning(
                "Failed to get cluster status: %s", e
            )
            return {
                "cluster": cluster_name,
                "status": "unknown",
                "node_count": 0,
            }
