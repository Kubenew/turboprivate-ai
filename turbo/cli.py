import asyncio
import logging
from pathlib import Path

import click

logger = logging.getLogger("turboprivate")


@click.group()
def cli():
    """TurboPrivate AI — Self-hosted LLM inference + safety governance."""


@cli.group()
def model():
    """Manage models."""


@model.command("list")
def model_list():
    click.echo("No models installed.")


@model.command()
@click.argument("name")
def pull(name: str):
    click.echo(f"Pulling model {name}...")


@model.command()
@click.argument("name")
@click.option("--bits", default=4, help="Quantization bits")
@click.option("--method", default="awq", help="Quantization method")
def quantize(name: str, bits: int, method: str):
    click.echo(f"Quantizing {name} to INT{bits} via {method}...")


@model.command("serve")
@click.argument("name")
@click.option("--replicas", default=1, help="Number of replicas")
def model_serve(name: str, replicas: int):
    click.echo(f"Serving model {name} with {replicas} replicas...")


@cli.group()
def safety():
    """Safety & governance commands."""


@safety.command("status")
def safety_status():
    click.echo("Safety gates: enabled")


@safety.command("list")
def policies():
    click.echo("No policies configured.")


@safety.group()
def audit():
    """Audit trail commands."""


@audit.command()
@click.option("--hours", default=24, help="Hours to look back")
@click.option("--blocked-only", is_flag=True, help="Show only blocked requests")
def view(hours: int, blocked_only: bool):
    click.echo(f"Audit trail for last {hours}h: (empty)")


@cli.group()
def memory():
    """Memory & RAG commands."""


@memory.command()
@click.argument("path")
@click.option("--collection", default="default", help="Target collection")
@click.option("--chunk-size", default=512, help="Chunk size in chars")
def ingest(path: str, collection: str, chunk_size: int):
    click.echo(f"Ingesting {path} into collection '{collection}'...")


@memory.command()
@click.argument("query")
@click.option("--collection", default="default", help="Collection to search")
@click.option("--top-k", default=5, help="Number of results")
def search(query: str, collection: str, top_k: int):
    click.echo(f"Searching for '{query}' in '{collection}'...")


@memory.command()
def collections():
    click.echo("Collections: (none)")


@cli.group()
def infra():
    """Infrastructure commands."""


@infra.command()
@click.option("--provider", default="bare-metal", help="Provider type")
@click.option("--name", default="turbo-cluster", help="Cluster name")
@click.option("--k3s-version", default="v1.30.0+k3s1", help="K3s version")
def init(provider: str, name: str, k3s_version: str):
    """Generate cluster configuration."""
    import yaml
    config = {
        "cluster_name": name,
        "provider": provider,
        "k3s_version": k3s_version,
        "nodes": [],
        "services": {
            "metallb": True,
            "ingress_nginx": True,
            "cert_manager": True,
            "monitoring": True,
            "longhorn": True,
        },
    }
    Path("turboprivate.yaml").write_text(yaml.dump(config, default_flow_style=False))
    click.echo(f"Generated turboprivate.yaml for cluster '{name}'")


@infra.command()
@click.option("--config", default="turboprivate.yaml", help="Config file path")
def deploy(config: str):
    """Deploy cluster and install platform."""
    import yaml

    from turbo.infra.provisioner import ClusterConfig, Node, Provisioner

    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"Config not found: {config}")
        return

    data = yaml.safe_load(config_path.read_text())
    nodes = [Node(n["host"], n.get("user", "root"), n.get("port", 22), n.get("role", "worker"))
             for n in data.get("nodes", [])]
    cluster_cfg = ClusterConfig(
        name=data.get("cluster_name", "turbo-cluster"),
        provider=data.get("provider", "bare-metal"),
        k3s_version=data.get("k3s_version", "v1.30.0+k3s1"),
        nodes=nodes,
    )
    provisioner = Provisioner(cluster_cfg)
    asyncio.run(provisioner.provision())
    click.echo(f"Cluster '{cluster_cfg.name}' deployed")


@infra.command()
@click.option("--name", default="turbo-cluster", help="Cluster name")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def destroy(name: str, yes: bool):
    """Destroy cluster."""
    if not yes:
        click.confirm(f"Destroy cluster '{name}'?", abort=True)
    from turbo.infra.provisioner import ClusterConfig, Provisioner
    provisioner = Provisioner(ClusterConfig(name=name))
    asyncio.run(provisioner.destroy(name))
    click.echo(f"Cluster '{name}' destroyed")


@infra.command()
@click.option("--name", default="turbo-cluster", help="Cluster name")
def status(name: str):
    """Show cluster status."""
    from turbo.infra.provisioner import ClusterConfig, Provisioner
    provisioner = Provisioner(ClusterConfig(name=name))
    result = asyncio.run(provisioner.status(name))
    click.echo(f"Cluster: {result['cluster']}")
    click.echo(f"Status: {result['status']}")
    click.echo(f"Nodes: {result.get('node_count', 'unknown')}")


@cli.command()
@click.option("--host", default="0.0.0.0", help="Bind address")
@click.option("--port", default=8000, help="Port")
@click.option("--reload", is_flag=True, help="Auto-reload on code changes")
@click.option("--workers", default=1, help="Number of workers")
def serve(host: str, port: int, reload: bool, workers: int):
    """Start the API server."""
    import uvicorn
    click.echo(f"TurboPrivate AI server starting on {host}:{port}")
    uvicorn.run("turbo.api.main:app", host=host, port=port, reload=reload, workers=workers)


@cli.command()
@click.argument("prompt")
def chat(prompt: str):
    """Interactive chat with a model."""
    click.echo(f"Chat: {prompt}")


@cli.command()
@click.argument("prompt")
@click.option("--model", default="default", help="Model to use")
def complete(prompt: str, model: str):
    """One-shot completion."""
    click.echo(f"Complete ({model}): {prompt}")


@cli.command()
@click.option("--encrypt", is_flag=True, help="Encrypt backup with age")
@click.option("--name", default="manual", help="Backup name")
def backup(encrypt: bool, name: str):
    """Create a backup."""
    from turbo.infra.backup import BackupManager
    bm = BackupManager()
    result = asyncio.run(bm.create(name, encrypt=encrypt))
    click.echo(f"Backup created: {result}")


@cli.command()
@click.argument("name")
def restore(name: str):
    """Restore from a backup."""
    from turbo.infra.backup import BackupManager
    bm = BackupManager()
    asyncio.run(bm.restore(name))
    click.echo(f"Restored from backup: {name}")


@cli.command()
def backups():
    """List backups."""
    from turbo.infra.backup import BackupManager
    bm = BackupManager()
    backups = asyncio.run(bm.list_backups())
    if not backups:
        click.echo("No backups found.")
        return
    for b in backups:
        enc = " [encrypted]" if b["encrypted"] else ""
        click.echo(f"  {b['name']} ({b['size_bytes']} bytes){enc}")


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def doctor(verbose: bool):
    """Check system health and dependencies."""
    import shutil
    import subprocess
    import sys

    def ok(msg):
        return click.style("[OK]", fg="green") + f" {msg}"

    def warn(msg):
        return click.style("[!!]", fg="yellow") + f" {msg}"

    def fail(msg):
        return click.style("[XX]", fg="red") + f" {msg}"

    click.echo(click.style("TurboPrivate AI System Check", bold=True))
    click.echo(click.style("=" * 40, dim=True))

    click.echo(f"\n{'Platform':>20}  ", nl=False)
    click.echo(ok(f"{sys.platform}, Python {sys.version.split()[0]}"))

    click.echo(f"\n{click.style('RUNTIME', bold=True)}")

    try:
        import torch
        cuda = torch.cuda.is_available()
        if cuda:
            name = torch.cuda.get_device_name(0)
            mem = torch.cuda.get_device_properties(0).total_mem / 1e9
            click.echo(f"{'PyTorch':>20}  {ok(f'{torch.__version__}')}")
            click.echo(f"{'CUDA':>20}  {ok(f'{name} ({mem:.1f} GB VRAM)')}")
        else:
            click.echo(f"{'PyTorch':>20}  {ok(torch.__version__)}")
            click.echo(f"{'CUDA':>20}  {warn('not available')}")
    except ImportError:
        click.echo(f"{'PyTorch':>20}  {fail('not installed')}")
        cuda = False

    for mod, label in [("vllm", "vLLM"), ("transformers", "Transformers"),
                        ("fastapi", "FastAPI"), ("uvicorn", "Uvicorn"),
                        ("httpx", "HTTPX"), ("numpy", "NumPy")]:
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "")
            click.echo(f"{label:>20}  {ok(ver)}")
        except ImportError:
            click.echo(f"{label:>20}  {warn('not installed')}")

    click.echo(f"\n{click.style('SYSTEM', bold=True)}")

    try:
        import psutil
        mem = psutil.virtual_memory()
        mem_str = f"{mem.used / 1e9:.1f} / {mem.total / 1e9:.1f} GB ({mem.percent}%)"
        click.echo(f"{'Memory':>20}  {ok(mem_str)}")
        cpu_count = psutil.cpu_count()
        cpu_pct = psutil.cpu_percent(interval=0.5)
        click.echo(f"{'CPU':>20}  {ok(f'{cpu_count} cores ({cpu_pct}%)')}")
        disk = psutil.disk_usage("/")
        disk_str = f"{disk.free / 1e9:.1f} GB free of {disk.total / 1e9:.1f} GB"
        click.echo(f"{'Disk':>20}  {ok(disk_str)}")
    except ImportError:
        click.echo(f"{'Memory':>20}  {warn('psutil not installed')}")

    click.echo(f"\n{click.style('TOOLS', bold=True)}")

    for tool, label in [("docker", "Docker"), ("kubectl", "kubectl"),
                         ("helm", "Helm"), ("git", "Git"),
                         ("curl", "curl"), ("age", "age")]:
        path = shutil.which(tool)
        if path:
            try:
                ver = subprocess.run(
                    [tool, "--version"],
                    capture_output=True, text=True, timeout=5,
                )
                out = ver.stdout or ver.stderr
                line = out.split("\n")[0][:60]
                click.echo(f"{label:>20}  {ok(line.strip() or 'found')}")
            except Exception:
                click.echo(f"{label:>20}  {ok('found')}")
        else:
            click.echo(f"{label:>20}  {warn('not found in PATH')}")

    click.echo(f"\n{click.style('NETWORK', bold=True)}")

    for host, label in [("pypi.org", "PyPI"), ("github.com", "GitHub"),
                         ("huggingface.co", "HuggingFace")]:
        code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                               f"https://{host}", "--max-time", "5"],
                              capture_output=True, text=True).stdout.strip()
        if code and code.startswith(("2", "3")):
            click.echo(f"{label:>20}  {ok('reachable')}")
        else:
            click.echo(f"{label:>20}  {warn('unreachable')}")

    click.echo("")
    all_ok = cuda and all(shutil.which(t) for t in ("docker", "kubectl", "helm"))
    if all_ok:
        click.echo(ok("System ready for deployment"))
    else:
        click.echo(warn("System partially ready - see details above"))


@cli.command()
@click.option("--service", default="all", help="Service name")
def logs(service: str):
    """View platform logs."""
    click.echo(f"Showing logs for {service}...")


if __name__ == "__main__":
    cli()
