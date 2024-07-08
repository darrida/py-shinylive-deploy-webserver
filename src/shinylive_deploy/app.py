import click

from .process import initialize


@click.group()
def cli():
    ...


@cli.command()
@click.argument("deploy_mode")
def deploy(deploy_mode: str):
    shinylive_ = initialize(deploy_mode)
    shinylive_.deploy()


@cli.command()
@click.argument("deploy_mode")
def rollback(deploy_mode: str):
    shinylive_ = initialize(deploy_mode)
    shinylive_.rollback()


@cli.command()
@click.argument("deploy_mode")
def clean_rollback(deploy_mode: str):
    shinylive_ = initialize(deploy_mode)
    shinylive_.clean_rollback()


@cli.command()
@click.argument("deploy_mode")
def remove(deploy_mode: str):
    shinylive_ = initialize(deploy_mode)
    shinylive_.remove()
